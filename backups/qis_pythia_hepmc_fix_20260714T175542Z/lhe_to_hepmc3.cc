#include "qis/EventMetadata.h"
#include "qis/ShowerConfig.h"

#include "HepMC3/Attribute.h"
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

void add_metadata(HepMC3::GenEvent& event, const qis::ShowerConfig& config, std::int64_t index) {
  event.add_attribute("whizard_campaign_id", std::make_shared<HepMC3::StringAttribute>(config.campaign_id));
  event.add_attribute("whizard_sample_id", std::make_shared<HepMC3::StringAttribute>(config.sample_id));
  event.add_attribute("whizard_shard_id", std::make_shared<HepMC3::StringAttribute>(config.shard_id));
  event.add_attribute("whizard_event_index", std::make_shared<HepMC3::IntAttribute>(static_cast<int>(index)));
  event.add_attribute("pythia_seed", std::make_shared<HepMC3::IntAttribute>(static_cast<int>(config.seed)));
  event.add_attribute("top_decays_preserved_from_lhe", std::make_shared<HepMC3::IntAttribute>(1));
  event.add_attribute("incoming_lepton_isr_from_whizard", std::make_shared<HepMC3::IntAttribute>(1));
}
}  // namespace

int main(int argc, char** argv) {
  qis::RunSummary summary;
  try {
    const auto config = qis::parse_command_line(argc, argv);
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
    const auto partial_output = config.output_hepmc3.string() + ".partial";
    std::filesystem::remove(partial_output);

    Pythia8::Pythia pythia;
    if (!pythia.readFile(config.settings_file.string())) {
      throw std::runtime_error("PYTHIA failed to read settings file");
    }
    pythia.readString("Beams:LHEF = " + config.input_lhe.string());
    pythia.readString("Random:setSeed = on");
    pythia.readString("Random:seed = " + std::to_string(config.seed));
    for (const auto& setting : config.pythia_overrides) {
      if (!pythia.readString(setting)) throw std::runtime_error("invalid PYTHIA override: " + setting);
    }
    if (!pythia.init()) throw std::runtime_error("PYTHIA initialization failed");

    HepMC3::WriterAscii writer(partial_output);
    HepMC3::Pythia8ToHepMC3 converter;
    int consecutive_failures = 0;

    while (config.max_events < 0 || summary.accepted_events < config.max_events) {
      ++summary.attempted_events;
      if (!pythia.next()) {
        if (pythia.info.atEndOfFile()) break;
        ++summary.failed_events;
        ++consecutive_failures;
        if (!config.allow_failed_events || consecutive_failures >= config.max_consecutive_failures) {
          throw std::runtime_error("PYTHIA event generation failed before EOF");
        }
        continue;
      }
      consecutive_failures = 0;
      HepMC3::GenEvent event(HepMC3::Units::GEV, HepMC3::Units::MM);
      converter.fill_next_event(pythia, &event);
      event.set_event_number(static_cast<int>(summary.accepted_events));
      add_metadata(event, config, summary.accepted_events);
      writer.write_event(event);
      const double weight = pythia.info.weight();
      summary.weight_sum += weight;
      summary.weight_sum2 += weight * weight;
      ++summary.accepted_events;
    }
    writer.close();
    pythia.stat();
    summary.sigma_gen_mb = pythia.info.sigmaGen();
    summary.finished_utc = qis::utc_now();
    summary.return_code = 0;
    summary.status = "success";
    std::filesystem::rename(partial_output, config.output_hepmc3);
    qis::write_summary_json(summary, config.metadata_json);
    std::cout << "SHOWER SUCCESS sample=" << config.sample_id
              << " events=" << summary.accepted_events
              << " output=" << config.output_hepmc3 << '\n';
    return 0;
  } catch (const std::exception& error) {
    summary.finished_utc = qis::utc_now();
    summary.return_code = 1;
    summary.status = "failed";
    std::cerr << "ERROR: " << error.what() << '\n';
    try {
      if (!summary.output_path.empty()) {
        const std::filesystem::path metadata = summary.output_path + ".metadata.json";
        qis::write_summary_json(summary, metadata);
      }
    } catch (...) {
    }
    return 1;
  }
}
