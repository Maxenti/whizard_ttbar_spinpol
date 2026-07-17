#pragma once

#include <cstdint>
#include <filesystem>
#include <string>

namespace qis {

struct RunSummary {
  std::string campaign_id;
  std::string sample_id;
  std::string shard_id;
  std::string input_path;
  std::string output_path;
  std::string settings_path;
  std::string pythia_version;
  std::string hepmc_version;
  std::string host;
  std::string started_utc;
  std::string finished_utc;
  std::uint32_t seed{0};
  std::int64_t requested_events{-1};
  std::int64_t attempted_events{0};
  std::int64_t accepted_events{0};
  std::int64_t failed_events{0};
  double sigma_gen_mb{0.0};
  double weight_sum{0.0};
  double weight_sum2{0.0};
  int return_code{0};
  std::string status{"unknown"};
};

std::string utc_now();
std::string hostname();
void write_summary_json(const RunSummary& summary, const std::filesystem::path& output);

}  // namespace qis
