#!/usr/bin/env python3
"""Wave 11 / E1: creates a *dump* variant of MappingEvolve's initial mockturtle `map` (mapping.hpp + initial operators).
The released sources are only read. The patch adds one member function and one call site. After the mapper's own passes
(execute_mapping) and before buffer insertion, if the environment variable C1_DUMP names a file, the full cut-match space
is written as JSON, together with the heuristic's final state:
  per gate node: every usable cut, every matching gate in each output phase (leaves, leaf polarities, pin delays per
  leaf, pin permutation, area, area flow under the final state), plus the node's final arrival/required/flows/refs and
  chosen match per phase.
No mapping decision is changed: the dump only reads state. Outputs go to experiments/inputs/e1_dump_variant/."""
import hashlib
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
W10 = os.path.normpath(os.path.join(ROOT, "..", "12_WAVE_10_EXPERIMENTAL_DISCOVERY"))
SRC = os.path.join(W10, "third_party", "MappingEvolve", "mapping")
OUT = os.path.join(ROOT, "experiments", "inputs", "e1_dump_variant")
os.makedirs(OUT, exist_ok=True)

hpp = open(os.path.join(SRC, "mapping.hpp"), encoding="utf-8").read()

inc_anchor = "#include <cstdint>\n"
assert hpp.count(inc_anchor) == 1
hpp = hpp.replace(inc_anchor, inc_anchor + "#include <cstdlib>\n#include <fstream>\n#include <map>\n#include <sstream>\n", 1)

call_anchor = """        /* execute mapping */
        if (!execute_mapping())
          return res;
"""
assert hpp.count(call_anchor) == 1, "call anchor"
hpp = hpp.replace(call_anchor, call_anchor + "\n        /* Wave 11 E1: read-only dump of the search space and final state */\n        c1_dump_if_requested();\n", 1)

func = r'''
      /* Wave 11 E1: read-only dump of the cut-match space and the heuristic's final state (JSON). */
      void c1_dump_if_requested() {
        const char *path = std::getenv("C1_DUMP");
        if (path == nullptr)
          return;
        std::ostringstream nodes;
        nodes.precision(12);
        std::map<uint32_t, gate const *> used;
        bool first_node = true;
        ntk.foreach_gate([&](auto const &n) {
          const auto index = ntk.node_to_index(n);
          auto const &nd = node_match[index];
          nodes << (first_node ? "" : ",") << "\n{\"i\":" << index;
          first_node = false;
          nodes << ",\"arr\":[" << nd.arrival[0] << "," << nd.arrival[1] << "]";
          nodes << ",\"req\":[" << nd.required[0] << "," << nd.required[1] << "]";
          nodes << ",\"flow\":[" << nd.flows[0] << "," << nd.flows[1] << "," << nd.flows[2] << "]";
          nodes << ",\"refs\":[" << nd.map_refs[0] << "," << nd.map_refs[1] << "," << nd.map_refs[2] << "]";
          nodes << ",\"same\":" << (nd.same_match ? 1 : 0);
          nodes << ",\"best\":[";
          for (uint8_t p = 0; p < 2; ++p) {
            if (p) nodes << ",";
            if (nd.best_supergate[p] == nullptr) {
              nodes << "null";
            } else {
              nodes << "[" << nd.best_cut[p] << "," << nd.best_supergate[p]->root->root->id << "," << (unsigned)nd.phase[p] << "]";
            }
          }
          nodes << "],\"cands\":[";
          bool first_cand = true;
          uint32_t cut_index = 0u;
          for (auto &cut : cuts.cuts(index)) {
            if ((*cut)->data.ignore) {
              ++cut_index;
              continue;
            }
            auto const &m = matches[index][(*cut)->data.match_index];
            for (uint8_t p = 0; p < 2; ++p) {
              if (m.supergates[p] == nullptr)
                continue;
              for (auto const &g : *m.supergates[p]) {
                if (g.root->is_super)
                  continue;
                const uint8_t pol = g.polarity ^ m.negations[p];
                double flow = g.area;
                std::ostringstream leaves, dl, pm;
                uint32_t ctr = 0u;
                for (auto l : *cut) {
                  flow += node_match[l].flows[(pol >> ctr) & 1];
                  leaves << (ctr ? "," : "") << l;
                  dl << (ctr ? "," : "") << g.tdelay[ctr];
                  pm << (ctr ? "," : "") << (unsigned)g.permutation[ctr];
                  ++ctr;
                }
                used[g.root->root->id] = g.root->root;
                nodes << (first_cand ? "" : ",") << "[" << (unsigned)p << "," << cut_index << ",[" << leaves.str() << "],"
                      << g.root->root->id << "," << g.area << "," << (unsigned)pol << ",[" << dl.str() << "],[" << pm.str() << "]," << flow << "]";
                first_cand = false;
              }
            }
            ++cut_index;
          }
          nodes << "]}";
        });
        std::ofstream os(path);
        os.precision(12);
        os << "{\"inv\":{\"id\":" << lib_inv_id << ",\"area\":" << lib_inv_area << ",\"delay\":" << lib_inv_delay << "}";
        os << ",\"buf\":{\"id\":" << lib_buf_id << ",\"area\":" << lib_buf_area << ",\"delay\":" << lib_buf_delay << "}";
        os << ",\"delay\":" << delay << ",\"area\":" << area << ",\"required_param\":" << ps.required_time;
        os << ",\"pis\":[";
        { bool f = true; ntk.foreach_pi([&](auto const &n) { os << (f ? "" : ",") << ntk.node_to_index(n); f = false; }); }
        os << "],\"pos\":[";
        { bool f = true; ntk.foreach_po([&](auto const &s) { os << (f ? "" : ",") << "[" << ntk.node_to_index(ntk.get_node(s)) << "," << (ntk.is_complemented(s) ? 1 : 0) << "]"; f = false; }); }
        os << "],\"gates\":{";
        { bool f = true;
          for (auto const &[id, gp] : used) {
            os << (f ? "" : ",") << "\"" << id << "\":[\"" << gp->name << "\",[";
            for (uint32_t j = 0; j < gp->pins.size(); ++j)
              os << (j ? "," : "") << "\"" << gp->pins[j].name << "\"";
            os << "]]";
            f = false;
          }
        }
        os << "},\"nodes\":[" << nodes.str() << "\n]}\n";
      }
'''
decl_anchor = "      void insert_buffers() {"
assert hpp.count(decl_anchor) == 1
hpp = hpp.replace(decl_anchor, func + "\n" + decl_anchor, 1)

open(os.path.join(OUT, "mapping.hpp"), "w", encoding="utf-8", newline="\n").write(hpp)
man = []
for f in ("match_phase.cpp", "match_phase_exact.cpp", "match_drop_phase.cpp"):
    s = open(os.path.join(SRC, f), encoding="utf-8").read()
    open(os.path.join(OUT, f), "w", encoding="utf-8", newline="\n").write(s)
    man.append("%s %s" % (hashlib.md5(s.encode()).hexdigest(), f))
man.append("%s %s (patched from %s)" % (hashlib.md5(hpp.encode()).hexdigest(), "mapping.hpp",
                                         hashlib.md5(open(os.path.join(SRC, "mapping.hpp"), encoding="utf-8").read().encode()).hexdigest()))
open(os.path.join(OUT, "MANIFEST.txt"), "w").write("\n".join(man) + "\n")
print("\n".join(man))
