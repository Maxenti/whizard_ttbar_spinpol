#include "qis/EventMetadata.h"
#include "qis/ShowerConfig.h"

#include "HepMC3/Attribute.h"
#include "HepMC3/GenCrossSection.h"
#include "HepMC3/GenEvent.h"
#include "HepMC3/Version.h"
#include "HepMC3/WriterAscii.h"
#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/HepMC3.h"

#include <cmath>
#include <filesystem>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <sstream>
#include <string>

namespace {
#define QIS_STRINGIFY_IMPL(value) #value
#define QIS_STRINGIFY(value) QIS_STRINGIFY_IMPL(value)

void add_metadata(HepMC3::GenEvent& event,
                  const qis::ShowerConfig& config,
                  std::int64_t index,
                  const Pythia8::Info& info,
                  double nominal_weight) {
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
  event.add_attribute("weight_policy", std::make_shared<HepMC3::StringAttribute>(
      "nominal_lha_weight_only; WHIZARD sqme_prc auxiliary weights are not propagated"));
}

void add_nominal_weight_and_cross_section(HepMC3::GenEvent& event,
                                          const Pythia8::Info& info,
                                          double nominal_weight) {
  // WHIZARD writes an auxiliary <weight name="sqme_prc"> value without a
  // corresponding LHE <initrwgt> declaration.  PYTHIA 8.315 can expose an
  // inconsistent multiweight count for such files, and the stock HepMC3
  // converter then performs an out-of-range access.  These production files
  // are unweighted (XWGTUP = 1), so the physically relevant event weight is
  // the nominal LHA weight returned by info.weight().  Store exactly that one
  // weight and construct the cross-section object explicitly.
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

    std::filesystem::create_directories(config.output_hepmc3.parent_path());
    std::filesystem::create_directories(config.metadata_json.parent_path());
    std::filesystem::remove(partial_output_path);

    Pythia8::Pythia pythia;
    if (!pythia.readFile(config.settings_file.string())) {
      throw std::runtime_error("PYTHIA failed to read settings file");
    }
    if (!pythia.readString("Beams:LHEF = " + config.input_lhe.string())) {
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
    if (!pythia.init()) {
      throw std::runtime_error("PYTHIA initialization failed");
    }

    HepMC3::WriterAscii writer(partial_output_path.string());
    HepMC3::Pythia8ToHepMC3 converter;
    converter.set_store_pdf(false);
    converter.set_store_proc(false);
    converter.set_store_xsec(false);
    converter.set_store_weights(false);

    int consecutive_failures = 0;

    while (config.max_events < 0 || summary.accepted_events < config.max_events) {
      ++summary.attempted_events;
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
      const double nominal_weight = pythia.info.weight();
      HepMC3::GenEvent event(HepMC3::Units::GEV, HepMC3::Units::MM);

      // Deliberately pass no Info pointer to the stock converter.  The event
      // topology conversion is retained, while all fragile LHE multiweight
      // bookkeeping is handled explicitly below.
      const bool converted = converter.fill_next_event(
          pythia.event,
          &event,
          static_cast<int>(summary.accepted_events),
          nullptr,
          &pythia.settings);
      if (!converted) {
        throw std::runtime_error("PYTHIA-to-HepMC3 topology conversion failed");
      }

      add_nominal_weight_and_cross_section(event, pythia.info, nominal_weight);
      add_metadata(event, config, summary.accepted_events, pythia.info, nominal_weight);
      writer.write_event(event);
      if (writer.failed()) {
        throw std::runtime_error("HepMC3 writer failed while writing " + partial_output_path.string());
      }

      summary.weight_sum += nominal_weight;
      summary.weight_sum2 += nominal_weight * nominal_weight;
      ++summary.accepted_events;
    }

    writer.close();
    if (writer.failed()) {
      throw std::runtime_error("HepMC3 writer failed while closing " + partial_output_path.string());
    }

    if (summary.accepted_events == 0) {
      throw std::runtime_error("no events were accepted from the LHE input");
    }
    if (config.max_events > 0 && summary.accepted_events != config.max_events) {
      std::ostringstream message;
      message << "LHE input ended after " << summary.accepted_events
              << " accepted events; requested " << config.max_events;
      throw std::runtime_error(message.str());
    }

    pythia.stat();
    summary.sigma_gen_mb = pythia.info.sigmaGen();
    summary.finished_utc = qis::utc_now();
    summary.return_code = 0;
    summary.status = "success";
    summary.error_message.clear();

    std::filesystem::remove(config.output_hepmc3);
    std::filesystem::rename(partial_output_path, config.output_hepmc3);
    qis::write_summary_json(summary, metadata_path);

    std::cout << "SHOWER SUCCESS sample=" << config.sample_id
              << " events=" << summary.accepted_events
              << " output=" << config.output_hepmc3 << '\n';
    return 0;
  } catch (const std::exception& error) {
    summary.finished_utc = qis::utc_now();
    summary.return_code = 1;
    summary.status = "failed";
    summary.error_message = error.what();
    std::cerr << "ERROR: " << error.what() << '\n';

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
