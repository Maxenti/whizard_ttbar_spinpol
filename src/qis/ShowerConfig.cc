#include "qis/ShowerConfig.h"

#include <charconv>
#include <sstream>
#include <stdexcept>

namespace qis {
namespace {

template <typename T>
T parse_integer(const std::string& value, const std::string& option) {
  T result{};
  const auto* begin = value.data();
  const auto* end = begin + value.size();
  const auto [ptr, ec] = std::from_chars(begin, end, result);
  if (ec != std::errc{} || ptr != end) {
    throw std::invalid_argument("invalid integer for " + option + ": " + value);
  }
  return result;
}

std::string require_value(int& index, int argc, char** argv, const std::string& option) {
  if (index + 1 >= argc) {
    throw std::invalid_argument("missing value after " + option);
  }
  ++index;
  return argv[index];
}

}  // namespace

std::string usage(const char* argv0) {
  std::ostringstream out;
  out << "Usage: " << argv0 << " --input FILE.lhe --output FILE.hepmc3 --settings FILE.cmnd\n"
      << "       --sample-id ID --campaign-id ID [options]\n\n"
      << "Options:\n"
      << "  --metadata FILE.json          Run-summary JSON output (default: OUTPUT.metadata.json)\n"
      << "  --shard-id ID                 Shard identifier (default: merged)\n"
      << "  --max-events N                Stop after N accepted events; -1 means all\n"
      << "  --seed N                      PYTHIA random seed in [1,900000000]\n"
      << "  --set 'Pythia:setting = x'    Additional PYTHIA setting; repeatable\n"
      << "  --allow-failed-events         Continue after isolated pythia.next() failures\n"
      << "  --max-consecutive-failures N  Abort threshold (default: 10)\n"
      << "  -h, --help                    Show this message\n";
  return out.str();
}

ShowerConfig parse_command_line(int argc, char** argv) {
  ShowerConfig config;
  for (int i = 1; i < argc; ++i) {
    const std::string option = argv[i];
    if (option == "-h" || option == "--help") {
      throw std::runtime_error(usage(argv[0]));
    } else if (option == "--input") {
      config.input_lhe = require_value(i, argc, argv, option);
    } else if (option == "--output") {
      config.output_hepmc3 = require_value(i, argc, argv, option);
    } else if (option == "--settings") {
      config.settings_file = require_value(i, argc, argv, option);
    } else if (option == "--metadata") {
      config.metadata_json = require_value(i, argc, argv, option);
    } else if (option == "--sample-id") {
      config.sample_id = require_value(i, argc, argv, option);
    } else if (option == "--campaign-id") {
      config.campaign_id = require_value(i, argc, argv, option);
    } else if (option == "--shard-id") {
      config.shard_id = require_value(i, argc, argv, option);
    } else if (option == "--max-events") {
      config.max_events = parse_integer<std::int64_t>(require_value(i, argc, argv, option), option);
    } else if (option == "--seed") {
      config.seed = parse_integer<std::uint32_t>(require_value(i, argc, argv, option), option);
    } else if (option == "--max-consecutive-failures") {
      config.max_consecutive_failures = parse_integer<int>(require_value(i, argc, argv, option), option);
    } else if (option == "--set") {
      config.pythia_overrides.push_back(require_value(i, argc, argv, option));
    } else if (option == "--allow-failed-events") {
      config.allow_failed_events = true;
    } else {
      throw std::invalid_argument("unknown option: " + option + "\n" + usage(argv[0]));
    }
  }
  if (config.metadata_json.empty() && !config.output_hepmc3.empty()) {
    config.metadata_json = config.output_hepmc3.string() + ".metadata.json";
  }
  validate_config(config);
  return config;
}

void validate_config(const ShowerConfig& config) {
  if (config.input_lhe.empty() || config.output_hepmc3.empty() || config.settings_file.empty()) {
    throw std::invalid_argument("--input, --output, and --settings are required");
  }
  if (config.sample_id.empty() || config.campaign_id.empty()) {
    throw std::invalid_argument("--sample-id and --campaign-id are required");
  }
  if (!std::filesystem::is_regular_file(config.input_lhe)) {
    throw std::invalid_argument("input LHE does not exist: " + config.input_lhe.string());
  }
  if (!std::filesystem::is_regular_file(config.settings_file)) {
    throw std::invalid_argument("PYTHIA settings file does not exist: " + config.settings_file.string());
  }
  if (config.seed < 1 || config.seed > 900000000U) {
    throw std::invalid_argument("PYTHIA seed must lie in [1,900000000]");
  }
  if (config.max_events == 0 || config.max_events < -1) {
    throw std::invalid_argument("--max-events must be -1 or a positive integer");
  }
  if (config.max_consecutive_failures < 1) {
    throw std::invalid_argument("--max-consecutive-failures must be positive");
  }
}

}  // namespace qis
