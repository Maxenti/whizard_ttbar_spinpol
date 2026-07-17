#pragma once

#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <vector>

namespace qis {

struct ShowerConfig {
  std::filesystem::path input_lhe;
  std::filesystem::path output_hepmc3;
  std::filesystem::path settings_file;
  std::filesystem::path metadata_json;
  std::string sample_id;
  std::string campaign_id;
  std::string shard_id{"merged"};
  std::int64_t max_events{-1};
  std::uint32_t seed{1};
  bool allow_failed_events{false};
  int max_consecutive_failures{10};
  std::vector<std::string> pythia_overrides;
};

ShowerConfig parse_command_line(int argc, char** argv);
std::string usage(const char* argv0);
void validate_config(const ShowerConfig& config);

}  // namespace qis
