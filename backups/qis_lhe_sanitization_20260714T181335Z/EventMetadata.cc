#include "qis/EventMetadata.h"

#include <chrono>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <unistd.h>

namespace qis {
namespace {
std::string escape_json(const std::string& text) {
  std::ostringstream out;
  for (const char ch : text) {
    switch (ch) {
      case '\\': out << "\\\\"; break;
      case '"': out << "\\\""; break;
      case '\n': out << "\\n"; break;
      case '\r': out << "\\r"; break;
      case '\t': out << "\\t"; break;
      default: out << ch; break;
    }
  }
  return out.str();
}
}  // namespace

std::string utc_now() {
  const auto now = std::chrono::system_clock::now();
  const std::time_t time = std::chrono::system_clock::to_time_t(now);
  std::tm tm{};
  gmtime_r(&time, &tm);
  std::ostringstream out;
  out << std::put_time(&tm, "%Y-%m-%dT%H:%M:%SZ");
  return out.str();
}

std::string hostname() {
  char buffer[256]{};
  if (::gethostname(buffer, sizeof(buffer) - 1) != 0) return "unknown";
  return buffer;
}

void write_summary_json(const RunSummary& s, const std::filesystem::path& output) {
  std::filesystem::create_directories(output.parent_path());
  const auto temporary = output.string() + ".tmp." + std::to_string(::getpid());
  std::ofstream out(temporary);
  if (!out) throw std::runtime_error("cannot create metadata file: " + temporary);
  out << std::setprecision(17)
      << "{\n"
      << "  \"schema_version\": 1,\n"
      << "  \"campaign_id\": \"" << escape_json(s.campaign_id) << "\",\n"
      << "  \"sample_id\": \"" << escape_json(s.sample_id) << "\",\n"
      << "  \"shard_id\": \"" << escape_json(s.shard_id) << "\",\n"
      << "  \"input_path\": \"" << escape_json(s.input_path) << "\",\n"
      << "  \"output_path\": \"" << escape_json(s.output_path) << "\",\n"
      << "  \"settings_path\": \"" << escape_json(s.settings_path) << "\",\n"
      << "  \"pythia_version\": \"" << escape_json(s.pythia_version) << "\",\n"
      << "  \"hepmc_version\": \"" << escape_json(s.hepmc_version) << "\",\n"
      << "  \"host\": \"" << escape_json(s.host) << "\",\n"
      << "  \"started_utc\": \"" << escape_json(s.started_utc) << "\",\n"
      << "  \"finished_utc\": \"" << escape_json(s.finished_utc) << "\",\n"
      << "  \"error_message\": \"" << escape_json(s.error_message) << "\",\n"
      << "  \"seed\": " << s.seed << ",\n"
      << "  \"requested_events\": " << s.requested_events << ",\n"
      << "  \"attempted_events\": " << s.attempted_events << ",\n"
      << "  \"accepted_events\": " << s.accepted_events << ",\n"
      << "  \"failed_events\": " << s.failed_events << ",\n"
      << "  \"sigma_gen_mb\": " << s.sigma_gen_mb << ",\n"
      << "  \"weight_sum\": " << s.weight_sum << ",\n"
      << "  \"weight_sum2\": " << s.weight_sum2 << ",\n"
      << "  \"return_code\": " << s.return_code << ",\n"
      << "  \"status\": \"" << escape_json(s.status) << "\"\n"
      << "}\n";
  out.close();
  std::filesystem::rename(temporary, output);
}

}  // namespace qis
