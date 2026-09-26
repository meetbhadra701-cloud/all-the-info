#!/usr/bin/env python3
"""D2 cause isolation: builds two ablation variants of the GPT-5 it29 operators by exact, asserted substitution.
The released sources are only read.
  ab1 = GPT-5 it29 with its delay-round changes reverted (area-round changes kept)
        match_phase: gpt5, with the !DO_AREA branch restored; match_drop_phase: initial
        (its only gpt5 change is in the delay branch); match_phase_exact: gpt5.
  ab2 = initial operators plus only GPT-5's delay-round changes
        match_phase: initial, with gpt5's !DO_AREA branch; match_drop_phase: gpt5; match_phase_exact: initial.
Writes experiments/inputs/c1/ablation/{ab1,ab2}/*.cpp and a manifest."""
import hashlib, os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
ME = os.path.join(ROOT, "third_party", "MappingEvolve")
INI = os.path.join(ME, "mapping")
GPT = os.path.join(ME, "output", "proactive_evolve_openevolve_gpt-5-2025-08-07_20251116_134740", "iter_29", "evolved_mapping")
OUT = os.path.join(ROOT, "experiments", "inputs", "c1", "ablation")
rd = lambda d, f: open(os.path.join(d, f), encoding="utf-8").read()
DELAY_GPT = ("          const double area_tol = 0.25 * static_cast<double>(lib_inv_area);\n"
             "          if (worst_arrival < best_arrival - epsilon) {\n"
             "            flag_compare_map = ((area_local <= best_area_flow + area_tol) || (worst_arrival <= best_arrival - 0.5 * static_cast<double>(lib_inv_delay)));\n")
DELAY_INI = ("          if (worst_arrival < best_arrival - epsilon) {\n"
             "            flag_compare_map = true;\n")
ini_mp, gpt_mp = rd(INI, "match_phase.cpp"), rd(GPT, "match_phase.cpp")
assert gpt_mp.count(DELAY_GPT) == 1
anchor = "        } else {\n" + DELAY_INI
assert ini_mp.count(anchor) == 1, "initial delay branch anchor not unique"
files = {
    "ab1": {"match_phase.cpp": gpt_mp.replace(DELAY_GPT, DELAY_INI),
            "match_drop_phase.cpp": rd(INI, "match_drop_phase.cpp"),
            "match_phase_exact.cpp": rd(GPT, "match_phase_exact.cpp")},
    "ab2": {"match_phase.cpp": ini_mp.replace(anchor, "        } else {\n" + DELAY_GPT),
            "match_drop_phase.cpp": rd(GPT, "match_drop_phase.cpp"),
            "match_phase_exact.cpp": rd(INI, "match_phase_exact.cpp")},
}
# sanity: ab1's delay branch must equal initial's, and its area branch must equal gpt5's; ab2 the reverse
assert files["ab1"]["match_phase.cpp"].count(DELAY_GPT) == 0 and "area_slack" in files["ab1"]["match_phase.cpp"]
assert files["ab2"]["match_phase.cpp"].count(DELAY_GPT) == 1 and "area_slack" not in files["ab2"]["match_phase.cpp"]
man = []
for v, fs in files.items():
    os.makedirs(os.path.join(OUT, v), exist_ok=True)
    for f, s in fs.items():
        open(os.path.join(OUT, v, f), "w", encoding="utf-8", newline="\n").write(s)
        man.append("%s %s %s" % (v, hashlib.md5(s.encode()).hexdigest(), f))
open(os.path.join(OUT, "MANIFEST.txt"), "w").write("\n".join(man) + "\n")
print("\n".join(man))
