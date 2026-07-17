#include "qis/EventMetadata.h"
#include "qis/ShowerConfig.h"

#include "HepMC3/Attribute.h"
#include "HepMC3/GenCrossSection.h"
#include "HepMC3/GenEvent.h"
#include "HepMC3/Version.h"
#include "HepMC3/WriterAscii.h"
#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/HepMC3.h"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <unistd.h>
#include <vector>

namespace {
#define QIS_STRINGIFY_IMPL(value) #value
#define QIS_STRINGIFY(value) QIS_STRINGIFY_IMPL(value)

struct PreparedLheInput {
  std::filesystem::path path;
  std::filesystem::path temporary_path;
  std::int64_t removed_sqme_weight_tags{0};

  bool sanitized() const { return !temporary_path.empty(); }

  ~PreparedLheInput() {
    if (!temporary_path.empty()) {
      std::error_code error;
      std::filesystem::remove(temporary_path, error);
    }
  }
};

bool contains_sqme_weight_open(const std::string& line) {
  const auto open = line.find("<weight");
  if (open == std::string::npos) return false;
  const auto close = line.find('>', open);
  if (close == std::string::npos) return false;
  const std::string tag = line.substr(open, close - open + 1);
  return tag.find("name=\"sqme_prc\"") != std::string::npos ||
         tag.find("name='sqme_prc'") != std::string::npos;
}

PreparedLheInput prepare_lhe_for_pythia(const std::filesystem::path& input,
                                        const std::filesystem::path& work_directory) {
  PreparedLheInput prepared;
  prepared.path = input;

  std::ifstream source(input);
  if (!source) {
    throw std::runtime_error("cannot open LHE input for sanitization scan: " + input.string());
  }

  const auto candidate = work_directory /
      ("." + input.filename().string() + ".pythia_sanitized." +
       std::to_string(::getpid()) + ".lhe");
  std::ofstream destination(candidate, std::ios::trunc);
  if (!destination) {
    throw std::runtime_error("cannot create temporary sanitized LHE: " + candidate.string());
  }

  bool skipping_sqme_weight = false;
  std::string line;
  while (std::getline(source, line)) {
    if (!skipping_sqme_weight && contains_sqme_weight_open(line)) {
      ++prepared.removed_sqme_weight_tags;
      if (line.find("</weight>") == std::string::npos) {
        skipping_sqme_weight = true;
      }
      continue;
    }
    if (skipping_sqme_weight) {
      if (line.find("</weight>") != std::string::npos) {
        skipping_sqme_weight = false;
      }
      continue;
    }
    destination << line << '\n';
  }

  if (!source.eof() || !destination) {
    throw std::runtime_error("I/O failure while preparing LHE input for PYTHIA");
  }
  if (skipping_sqme_weight) {
    throw std::runtime_error("unterminated WHIZARD sqme_prc <weight> element in " + input.string());
  }

  destination.close();
  source.close();

  if (prepared.removed_sqme_weight_tags == 0) {
    std::error_code error;
    std::filesystem::remove(candidate, error);
    return prepared;
  }

  prepared.path = candidate;
  prepared.temporary_path = candidate;
  return prepared;
}

void validate_pythia_topology(const Pythia8::Event& event) {
  const int size = event.size();
  for (int particle_index = 0; particle_index < size; ++particle_index) {
    const auto mothers = event[particle_index].motherList();
    for (const int mother_index : mothers) {
      if (mother_index < 0 || mother_index >= size) {
        std::ostringstream message;
        message << "invalid PYTHIA mother index: particle=" << particle_index
                << " id=" << event[particle_index].id()
                << " mother=" << mother_index
                << " event_size=" << size;
        throw std::runtime_error(message.str());
      }
    }
  }
}

void add_metadata(HepMC3::GenEvent& event,
                  const qis::ShowerConfig& config,
                  std::int64_t index,
                  const Pythia8::Info& info,
                  double nominal_weight,
                  const PreparedLheInput& prepared) {
  event.add_attribute("whizard_campaign_id", std::make_shared<HepMC3::StringAttribute>(config.campaign_id));
  event.add_attribute("whizard_sample_id", std::make_shared<HepMC3::StringAttribute>(config.sample_id));
  event.add_attribute("whizard_shard_id", std::make_shared<HepMC3::StringAttribute>(config.shard_id));
  event.add_attribute("whizard_event_index", std::make_shared<HepMC3::IntAttribute>(static_cast<int>(index)));
  event.add_attribute("pythia_seed", std::make_shared<HepMC3::IntAttribute>(static_cast<int>(config.seed)));
  event.add_attribute("top_decays_preserved_from_lhe", std::make_shared<HepMC3::IntAttribute>(1));
  event.add_attribute("incoming_lepton_isr_from_whizard", std::make_shared<HepMC3::IntAttribute>(1));
  event.add_attribute("signal_process_id", std::make_shared<HepMC3::IntAttribute>(info.code()));
  event.add_attribute("event_scale", std::make_shared<HepMC3::DoubleAttribute>(info.QRen()));
  event.add_attribute("alphaQCD", std::make_shared<HepMC3::DoubleAttribute>(info.alphaS()));
  event.add_attribute("alphaQED", std::make_shared<HepMC3::DoubleAttribute>(info.alphaEM()));
  event.add_attribute("nominal_event_weight", std::make_shared<HepMC3::DoubleAttribute>(nominal_weight));
  event.add_attribute("input_lhe_sanitized", std::make_shared<HepMC3::IntAttribute>(prepared.sanitized() ? 1 : 0));
  event.add_attribute("removed_sqme_prc_weight_tags", std::make_shared<HepMC3::IntAttribute>(
      static_cast<int>(prepared.removed_sqme_weight_tags)));
  event.add_attribute("weight_policy", std::make_shared<HepMC3::StringAttribute>(
      "nominal_lha_weight_only; WHIZARD sqme_prc auxiliary diagnostics removed before PYTHIA"));
}

void add_nominal_weight_and_cross_section(HepMC3::GenEvent& event,
                                          const Pythia8::Info& info,
                                          double nominal_weight) {
  event.weights().clear();
  event.weights().push_back(nominal_weight);

  auto cross_section = std::make_shared<HepMC3::GenCrossSection>();
  event.set_cross_section(cross_section);
  cross_section->set_cross_section(info.sigmaGen() * 1.0e9,
                                   info.sigmaErr() * 1.0e9);
}

}  // namespace

int main(int argc, char** argv) {
  qis::RunSummary summary;
  std::filesystem::path metadata_path;
  std::filesystem::path partial_output_path;
  std::string stage = "command-line parsing";

  try {
    const auto config = qis::parse_command_line(argc, argv);
    metadata_path = config.metadata_json;
    partial_output_path = config.output_hepmc3.string() + ".partial";

    summary.campaign_id = config.campaign_id;
    summary.sample_id = config.sample_id;
    summary.shard_id = config.shard_id;
    summary.input_path = std::filesystem::absolute(config.input_lhe).string();
    summary.output_path = std::filesystem::absolute(config.output_hepmc3).string();
    summary.settings_path = std::filesystem::absolute(config.settings_file).string();
    summary.seed = config.seed;
    summary.requested_events = config.max_events;
    summary.host = qis::hostname();
    summary.started_utc = qis::utc_now();
    summary.pythia_version = QIS_STRINGIFY(PYTHIA_VERSION);
    summary.hepmc_version = HepMC3::version();

    stage = "output-directory preparation";
    std::filesystem::create_directories(config.output_hepmc3.parent_path());
    std::filesystem::create_directories(config.metadata_json.parent_path());
    std::filesystem::remove(partial_output_path);

    stage = "WHIZARD auxiliary-weight sanitization";
    auto prepared_input = prepare_lhe_for_pythia(
        config.input_lhe, config.output_hepmc3.parent_path());
    summary.pythia_input_path = std::filesystem::absolute(prepared_input.path).string();
    summary.input_was_sanitized = prepared_input.sanitized();
    summary.removed_auxiliary_weight_tags = prepared_input.removed_sqme_weight_tags;

    stage = "PYTHIA settings initialization";
    Pythia8::Pythia pythia;
    if (!pythia.readFile(config.settings_file.string())) {
      throw std::runtime_error("PYTHIA failed to read settings file");
    }
    if (!pythia.readString("Beams:LHEF = " + prepared_input.path.string())) {
      throw std::runtime_error("PYTHIA rejected Beams:LHEF input path");
    }
    if (!pythia.readString("Random:setSeed = on") ||
        !pythia.readString("Random:seed = " + std::to_string(config.seed))) {
      throw std::runtime_error("PYTHIA rejected random-seed settings");
    }
    for (const auto& setting : config.pythia_overrides) {
      if (!pythia.readString(setting)) {
        throw std::runtime_error("invalid PYTHIA override: " + setting);
      }
    }

    stage = "PYTHIA init";
    if (!pythia.init()) {
      throw std::runtime_error("PYTHIA initialization failed");
    }

    stage = "HepMC3 writer initialization";
    HepMC3::WriterAscii writer(partial_output_path.string());
    HepMC3::Pythia8ToHepMC3 converter;
    converter.set_store_pdf(false);
    converter.set_store_proc(false);
    converter.set_store_xsec(false);
    converter.set_store_weights(false);

    int consecutive_failures = 0;

    while (config.max_events < 0 || summary.accepted_events < config.max_events) {
      ++summary.attempted_events;
      stage = "PYTHIA next event " + std::to_string(summary.attempted_events);
      if (!pythia.next()) {
        if (pythia.info.atEndOfFile()) {
          break;
        }
        ++summary.failed_events;
        ++consecutive_failures;
        if (!config.allow_failed_events ||
            consecutive_failures >= config.max_consecutive_failures) {
          throw std::runtime_error("PYTHIA event generation failed before EOF");
        }
        continue;
      }

      consecutive_failures = 0;
      summary.last_pythia_event_size = pythia.event.size();

      stage = "PYTHIA event-topology validation " + std::to_string(summary.attempted_events);
      validate_pythia_topology(pythia.event);

      stage = "nominal LHA weight retrieval " + std::to_string(summary.attempted_events);
      const double nominal_weight = pythia.info.weight();
      HepMC3::GenEvent event(HepMC3::Units::GEV, HepMC3::Units::MM);

      stage = "PYTHIA-to-HepMC3 topology conversion " + std::to_string(summary.attempted_events);
      const bool converted = converter.fill_next_event(
          pythia.event,
          &event,
          static_cast<int>(summary.accepted_events),
          nullptr,
          &pythia.settings);
      if (!converted) {
        throw std::runtime_error("PYTHIA-to-HepMC3 topology conversion failed");
      }

      stage = "HepMC3 metadata and weight population " + std::to_string(summary.attempted_events);
      add_nominal_weight_and_cross_section(event, pythia.info, nominal_weight);
      add_metadata(event, config, summary.accepted_events, pythia.info,
                   nominal_weight, prepared_input);

      stage = "HepMC3 event write " + std::to_string(summary.attempted_events);
      writer.write_event(event);
      if (writer.failed()) {
        throw std::runtime_error("HepMC3 writer failed while writing " + partial_output_path.string());
      }

      summary.weight_sum += nominal_weight;
      summary.weight_sum2 += nominal_weight * nominal_weight;
      ++summary.accepted_events;
    }

    stage = "HepMC3 writer close";
    writer.close();
    if (writer.failed()) {
      throw std::runtime_error("HepMC3 writer failed while closing " + partial_output_path.string());
    }

    stage = "accepted-event count validation";
    if (summary.accepted_events == 0) {
      throw std::runtime_error("no events were accepted from the LHE input");
    }
    if (config.max_events > 0 && summary.accepted_events != config.max_events) {
      std::ostringstream message;
      message << "LHE input ended after " << summary.accepted_events
              << " accepted events; requested " << config.max_events;
      throw std::runtime_error(message.str());
    }

    stage = "final statistics";
    pythia.stat();
    summary.sigma_gen_mb = pythia.info.sigmaGen();
    summary.finished_utc = qis::utc_now();
    summary.return_code = 0;
    summary.status = "success";
    summary.failure_stage.clear();
    summary.error_message.clear();

    stage = "atomic output finalization";
    std::filesystem::remove(config.output_hepmc3);
    std::filesystem::rename(partial_output_path, config.output_hepmc3);
    qis::write_summary_json(summary, metadata_path);

    std::cout << "SHOWER SUCCESS sample=" << config.sample_id
              << " events=" << summary.accepted_events
              << " sanitized=" << (summary.input_was_sanitized ? "yes" : "no")
              << " removed_sqme_prc=" << summary.removed_auxiliary_weight_tags
              << " output=" << config.output_hepmc3 << '\n';
    return 0;
  } catch (const std::exception& error) {
    summary.finished_utc = qis::utc_now();
    summary.return_code = 1;
    summary.status = "failed";
    summary.failure_stage = stage;
    summary.error_message = "stage=" + stage + ": " + error.what();
    std::cerr << "ERROR: " << summary.error_message << '\n';

    try {
      if (!partial_output_path.empty()) {
        std::filesystem::remove(partial_output_path);
      }
      if (!metadata_path.empty()) {
        qis::write_summary_json(summary, metadata_path);
      }
    } catch (const std::exception& metadata_error) {
      std::cerr << "ERROR: failed to write failure metadata: "
                << metadata_error.what() << '\n';
    }
    return 1;
  }
}
