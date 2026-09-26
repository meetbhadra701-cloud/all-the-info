// Wave 10 / C1 measurement driver (written for this study; not part of MappingEvolve).
// Compiled once per operator variant next to that variant's mapping.hpp, which
// #includes the variant's match_phase / match_phase_exact / match_drop_phase.
// Mapping parameters are identical to MappingEvolve's synthesis() in main.cpp,
// including the call form mockturtle::map(aig, lib, ps, &st). Two things are added:
// an optional required_time (0 means the mapper default: required = achieved delay)
// and the mapped netlist is written out for independent checking.
// The input AIG must already be preprocessed; the compress2 step runs outside this driver.
#include "mapping.hpp"

#include <lorina/aiger.hpp>
#include <lorina/genlib.hpp>
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
    std::fprintf(stderr, "usage: %s genlib in.aig out_prefix map|map_nodelay required_time\n", argv[0]);
    return 2;
  }
  const std::string genlib = argv[1], aig_path = argv[2], out = argv[3], mode = argv[4];
  const double required = std::atof(argv[5]);

  std::vector<mockturtle::gate> gates;
  if (lorina::read_genlib(genlib, mockturtle::genlib_reader(gates)) != lorina::return_code::success) return 3;
  mockturtle::tech_library_params tps;
  mockturtle::tech_library<5, mockturtle::classification_type::np_configurations> lib(gates, tps);

  mockturtle::aig_network aig;
  if (lorina::read_aiger(aig_path, mockturtle::aiger_reader(aig)) != lorina::return_code::success) return 4;

  mockturtle::map_params ps;
  ps.cut_enumeration_ps.minimize_truth_table = true;
  ps.cut_enumeration_ps.cut_limit = 16;
  ps.cut_enumeration_ps.cut_size = 6;
  ps.area_flow_rounds = 1;
  ps.ela_rounds = 2;
  ps.required_time = required;
  ps.skip_delay_round = (mode == "map_nodelay");
  mockturtle::map_stats st;
  auto res = mockturtle::map(aig, lib, ps, &st);

  mockturtle::write_verilog_with_binding(res, out + ".v");
  mockturtle::write_bench(res, out + ".bench");
  std::printf("{\"mapper\": \"%s\", \"area\": %.6f, \"delay\": %.6f, \"gates\": %u, \"depth\": %u, \"runtime\": %.6f, \"required\": %.6f, \"mapping_error\": %d, \"pis\": %u, \"pos\": %u, \"aig_gates\": %u}\n",
              mode.c_str(), st.area, st.delay, res.num_gates(), mockturtle::depth_view(res).depth(),
              std::chrono::duration<double>(st.time_total).count(), required, st.mapping_error ? 1 : 0,
              aig.num_pis(), aig.num_pos(), aig.num_gates());
  return 0;
}
