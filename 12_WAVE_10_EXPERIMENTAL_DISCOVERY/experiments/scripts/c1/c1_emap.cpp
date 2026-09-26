// Wave 10 / C1 stronger in-framework baseline: upstream mockturtle emap at the same
// mockturtle commit. The operators are unmodified and do not come from MappingEvolve.
// It uses the same cut limit and library object, and sets emap's own
// required_time and relax_required knobs.
#include <lorina/aiger.hpp>
#include <lorina/genlib.hpp>
#include <mockturtle/algorithms/emap.hpp>
#include <mockturtle/io/aiger_reader.hpp>
#include <mockturtle/io/genlib_reader.hpp>
#include <mockturtle/io/write_bench.hpp>
#include <mockturtle/io/write_verilog.hpp>
#include <mockturtle/networks/aig.hpp>
#include <mockturtle/views/depth_view.hpp>

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

int main(int argc, char *argv[]) {
  if (argc < 6) {
    std::fprintf(stderr, "usage: %s genlib in.aig out_prefix emap|emap_area required_time [relax_pct]\n", argv[0]);
    return 2;
  }
  const std::string genlib = argv[1], aig_path = argv[2], out = argv[3], mode = argv[4];
  const double required = std::atof(argv[5]);
  const double relax = argc > 6 ? std::atof(argv[6]) : 0.0;

  std::vector<mockturtle::gate> gates;
  if (lorina::read_genlib(genlib, mockturtle::genlib_reader(gates)) != lorina::return_code::success) return 3;
  mockturtle::tech_library_params tps;
  mockturtle::tech_library<5, mockturtle::classification_type::np_configurations> lib(gates, tps);

  mockturtle::aig_network aig;
  if (lorina::read_aiger(aig_path, mockturtle::aiger_reader(aig)) != lorina::return_code::success) return 4;

  mockturtle::emap_params ps;
  ps.cut_enumeration_ps.minimize_truth_table = true;
  ps.cut_enumeration_ps.cut_limit = 16;
  ps.required_time = required;
  ps.relax_required = relax;
  ps.area_oriented_mapping = (mode == "emap_area");
  mockturtle::emap_stats st;
  auto res = mockturtle::emap_klut(aig, lib, ps, &st);

  mockturtle::write_verilog_with_binding(res, out + ".v");
  mockturtle::write_bench(res, out + ".bench");
  std::printf("{\"mapper\": \"%s\", \"area\": %.6f, \"delay\": %.6f, \"gates\": %u, \"depth\": %u, \"runtime\": %.6f, \"required\": %.6f, \"relax\": %.3f, \"mapping_error\": %d, \"pis\": %u, \"pos\": %u, \"aig_gates\": %u}\n",
              mode.c_str(), st.area, st.delay, res.num_gates(), mockturtle::depth_view(res).depth(),
              std::chrono::duration<double>(st.time_total).count(), required, relax, st.mapping_error ? 1 : 0,
              aig.num_pis(), aig.num_pos(), aig.num_gates());
  return 0;
}
