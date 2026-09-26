# WAVE 6C-C — EAGERLYELASTIC × LSQ FRONTIER DOSSIER

## 1. Exact pinned compiler

Checkout:
/home/meetb/wave6cc/dynamatic-zenodo-exact

Pinned commit:

7d33a780b8907cd395065dc8a283836a3563418a

The checkout was verified clean at detached HEAD, with initialized recursive submodules. The required SpeculationV2 integration script, SpeculationV2 sources, golden-ratio fixture, and all five requested pass names were present. The compiler was built without Gurobi; the configured result was GUROBI_REQUIRED = NO. No Vivado, ModelSim, FPGA20, or aggregate interactive dynamatic executable was used.

## 2. Phase A successful baseline

Source:
/home/meetb/wave6cc/dynamatic-zenodo-exact/integration-test/golden_ratio/golden_ratio.c

Successful output:
/home/meetb/wave6cc/wave6cc-specv2-baseline-7d33a780/comp/handshake_post_speculation.mlir

This completed the compiler-semantic eager baseline through post-spec-v2.

## 3. Phase B — LSQ-only control

The first single_loop check completed but was only an ordinary memory-controller case: its independent arrays produced MC interfaces and no LSQ. It was not used as the qualifying LSQ control.

The qualifying source-backed LSQ-only control is:

/home/meetb/wave6cc/dynamatic-zenodo-exact/integration-test/loop_array/loop_array.c

The loop-carried same-region accesses are:

c[i - 1] load followed by c[i] store.

Saved pipeline directory:
/home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp

The C-to-Handshake commands were the pinned integration-driver flow:

~~~~sh
/home/meetb/wave6cc/dynamatic-zenodo-exact/polygeist/llvm-project/build/bin/clang -O0 -S -emit-llvm \
  /home/meetb/wave6cc/dynamatic-zenodo-exact/integration-test/loop_array/loop_array.c \
  -I /home/meetb/wave6cc/dynamatic-zenodo-exact/include \
  -Xclang -ffp-contract=off \
  -o /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/clang.ll

sed 's/optnone//g' \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/clang.ll \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/clang_optnone_removed.ll

/home/meetb/wave6cc/dynamatic-zenodo-exact/polygeist/llvm-project/build/bin/opt -S \
  -passes=mem2reg,instcombine,loop-rotate,consthoist,simplifycfg \
  -strip-debug \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/clang_optnone_removed.ll \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/clang_optimized.ll

/home/meetb/wave6cc/dynamatic-zenodo-exact/polygeist/llvm-project/build/bin/mlir-translate \
  --import-llvm \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/clang_optimized.ll \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/translated.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/translated.mlir \
  --remove-polygeist-attributes \
  --drop-unlisted-functions=function-names=loop_array \
  --allow-unregistered-dialect \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/removed_polygeist_attr.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/removed_polygeist_attr.mlir \
  "--convert-llvm-to-cf=source=/home/meetb/wave6cc/dynamatic-zenodo-exact/integration-test/loop_array/loop_array.c dynamatic-path=/home/meetb/wave6cc/dynamatic-zenodo-exact" \
  --remove-polygeist-attributes \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/cf.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/cf.mlir \
  --func-set-arg-names=source=/home/meetb/wave6cc/dynamatic-zenodo-exact/integration-test/loop_array/loop_array.c \
  --mark-memory-dependencies --flatten-memref-row-major --mark-memory-interfaces \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/cf_2.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/cf_2.mlir \
  --canonicalize --cse --sccp --symbol-dce --control-flow-sink \
  --loop-invariant-code-motion --canonicalize \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/cf_transformed.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/cf_transformed.mlir \
  --arith-reduce-strength=max-adder-depth-mul=1 --push-constants \
  --mark-memory-interfaces \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/cf_dyn_transformed.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/cf_dyn_transformed.mlir \
  --cf-gate-binarization \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/gate_binarized.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/gate_binarized.mlir \
  --lower-cf-to-handshake \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_before_lsq.mlir
~~~~

LSQ-only stage:

~~~~sh
/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_before_lsq.mlir \
  --handshake-analyze-lsq-usage \
  --handshake-replace-memory-interfaces \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_after_lsq.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_after_lsq.mlir \
  --handshake-minimize-cst-width --handshake-optimize-bitwidths \
  --handshake-materialize --handshake-infer-basic-blocks \
  --handshake-canonicalize \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_transformed.mlir
~~~~

All listed commands exited 0.

LSQ was actually instantiated before analysis/replacement:

~~~~text
handshake_before_lsq.mlir:3
%0:2 = lsq[%arg2 : memref<10xi32>] (..., %addressResult, %addressResult_6, %dataResult_7, ...) {groupSizes = [2 : i32], handshake.name = "lsq0"} ...

handshake_before_lsq.mlir:20
%addressResult, %dataResult = load[%11] %0#0 {handshake.bb = 1 : ui32, handshake.deps = #handshake<deps[["store0", 0]]>, handshake.name = "load0"} ...

handshake_before_lsq.mlir:24
%addressResult_6, %dataResult_7 = store[%14] %12 {handshake.bb = 1 : ui32, handshake.deps = #handshake<deps[["load0", 0]]>, handshake.name = "store0"} ...
~~~~

After LSQ analysis and interface replacement:

~~~~text
handshake_after_lsq.mlir:3
%0:2 = lsq[...] {groupSizes = [2 : i32], handshake.name = "lsq1"} ...

handshake_after_lsq.mlir:20
load0 ... handshake.mem_interface = #handshake.mem_interface<LSQ: 0> ...

handshake_after_lsq.mlir:24
store0 ... handshake.mem_interface = #handshake.mem_interface<LSQ: 0> ...
~~~~

Thus:

- LSQ count: 1.
- LSQ group: group 0, size 2.
- Load group member: load0.
- Store group member: store0.
- Load dependency: load0 -> store0.
- Store dependency: store0 -> load0.
- Memory interface replacement: both operations remain LSQ-backed, LSQ: 0.
- Allocation/order/control metadata: LSQ control inputs and outputs are present; the LSQ has the loop group control and memory-port channels, with group size [2].

## 4. Phase C — eager-only control

Source:
/home/meetb/wave6cc/dynamatic-zenodo-exact/integration-test/golden_ratio/golden_ratio.c

Input:
/home/meetb/wave6cc/wave6cc-specv2-baseline-7d33a780/comp/handshake_transformed.mlir

Saved stages:
/home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/handshake_pre_speculation.mlir
/home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/handshake_speculation.mlir
/home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/handshake_post_speculation.mlir

Commands:

~~~~sh
/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-specv2-baseline-7d33a780/comp/handshake_transformed.mlir \
  "--handshake-pre-spec-v2=json-path=/home/meetb/wave6cc/dynamatic-zenodo-exact/integration-test/golden_ratio/specv2.json" \
  --handshake-materialize --handshake-canonicalize \
  > /home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/handshake_pre_speculation.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/handshake_pre_speculation.mlir \
  "--handshake-speculation-v2=json-path=/home/meetb/wave6cc/dynamatic-zenodo-exact/integration-test/golden_ratio/specv2.json bb-mapping=/home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/bb_mapping.csv n=1" \
  --handshake-materialize --handshake-canonicalize \
  > /home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/handshake_speculation.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/handshake_speculation.mlir \
  --handshake-post-spec-v2 --handshake-materialize --handshake-canonicalize \
  > /home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/handshake_post_speculation.mlir
~~~~

All three commands exited 0.

The eager-only speculation stage contains:

~~~~text
%30 = spec_v2_repeating_init %28 {handshake.bb = 2 : ui32, handshake.name = "spec_v2_repeating_init0", initToken = 1 : ui1, specv2_top_ri = true}

%31:10 = fork [10] %30 ...
~~~~

The associated frontier/pass-through graph is present in the same stage and remains in post-speculation. There are no load, store, lsq, mem_controller, or mem_interface operations in this control. Eager/speculative transformation therefore executes independently of LSQ.

## 5. Phase D — combined LSQ plus eager case

Run-only metadata, derived from the executed loop block and not a source or compiler patch:

/home/meetb/wave6cc/wave6cc-phase-d-loop-array/loop_array_specv2.json

Contents:

~~~~json
{"spec-loop-bbs": [1]}
~~~~

Speculation commands:

~~~~sh
/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_transformed.mlir \
  "--handshake-pre-spec-v2=json-path=/home/meetb/wave6cc/wave6cc-phase-d-loop-array/loop_array_specv2.json" \
  --handshake-materialize --handshake-canonicalize \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_pre_speculation.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_pre_speculation.mlir \
  "--handshake-speculation-v2=json-path=/home/meetb/wave6cc/wave6cc-phase-d-loop-array/loop_array_specv2.json bb-mapping=/home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/bb_mapping.csv n=1" \
  --handshake-materialize --handshake-canonicalize \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_speculation.mlir

/home/meetb/wave6cc/dynamatic-zenodo-exact/build/bin/dynamatic-opt \
  /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_speculation.mlir \
  --handshake-post-spec-v2 --handshake-materialize --handshake-canonicalize \
  > /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_post_speculation.mlir
~~~~

All three commands exited 0.

The executed IR evidence is:

~~~~text
handshake_transformed.mlir:5
%2:2 = lsq[...] (..., %addressResult, %addressResult_6, %dataResult_7, %31) {groupSizes = [2 : i32], handshake.name = "lsq1"} ...

handshake_transformed.mlir:37
load0 ... handshake.deps = #handshake<deps[["store0", 0]]> handshake.mem_interface = #handshake.mem_interface<LSQ: 0> ...

handshake_transformed.mlir:39
store0 ... handshake.deps = #handshake<deps[["load0", 0]]> handshake.mem_interface = #handshake.mem_interface<LSQ: 0> ...

handshake_pre_speculation.mlir:5, 40, 42
The same LSQ, load0, and store0 remain, with the same group/dependency/interface metadata. Pre-spec adds passer/control wiring but does not remove or reroute the LSQ.

handshake_speculation.mlir:5
The same LSQ remains.

handshake_speculation.mlir:37-40
load0 and store0 remain LSQ-backed with mem_interface = #handshake.mem_interface<LSQ: 0>.

handshake_speculation.mlir:47
%35 = spec_v2_repeating_init %32 {handshake.bb = 1 : ui32, handshake.name = "spec_v2_repeating_init0", initToken = 1 : ui1, specv2_top_ri = true}

handshake_post_speculation.mlir:5, 33, 36, 43
The LSQ, load0, store0, LSQ interface attributes, and spec_v2_repeating_init all remain.
~~~~

Relevant SSA/control/memory edges in the final IR:

- load0 consumes address %22 and LSQ data channel %2#0.
- load0 produces addressResult and dataResult.
- dataResult feeds %24 = addi %dataResult, %41#1.
- %23 = passer %24[%32#3] places the load-derived data path under speculative/eager control.
- store0 consumes address %11 and data %23.
- store0 produces addressResult_6 and dataResult_7, which feed the LSQ ports.
- The LSQ remains the owner of the load/store memory ordering and group allocation path.
- The branch/loop control is block 1; bb_mapping.csv contains 0,0; 2,2; 1,1.

Narrow compiler observation: the LSQ-backed load is admitted into the same eager/speculative control graph. The LoadOp remains an LSQ operation; it is not replaced by a memory-controller operation and is not excluded.

## 6. Exact source-code boundary

There is no blocking condition in this pinned implementation for this combined specimen.

The exact relevant conditions are:

/home/meetb/wave6cc/dynamatic-zenodo-exact/experimental/lib/Transforms/SpeculationV2/SpecV2Lib.cpp:122-135

- getEffectiveOperands(LoadOp) returns the load address.
- getEffectiveResults(LoadOp) returns only the load data result, excluding memory-interface results.

/home/meetb/wave6cc/dynamatic-zenodo-exact/experimental/lib/Transforms/SpeculationV2/SpecV2Lib.cpp:191-204

isEligibleForPasserMotionOverPM explicitly includes LoadOp in the eligible operation set:

ArithOpInterface, NotOp, ForkOp, LazyForkOp, BufferOp, LoadOp, BranchOp.

There is no LSQOp, MemInterfaceAttr, LSQ-group, or memory-order rejection in this eligibility condition. Consequently, SpeculationV2 can move the load’s effective data/control frontier while the load remains connected to the LSQ.

/home/meetb/wave6cc/dynamatic-zenodo-exact/lib/Transforms/HandshakeAnalyzeLSQUsage.cpp:203-222

The LSQ analysis recognizes an existing LSQ interface and otherwise marks an MC-only region. It does not reject speculative control.

/home/meetb/wave6cc/dynamatic-zenodo-exact/lib/Transforms/HandshakeAnalyzeLSQUsage.cpp:224-307

It collects LSQ load/store groups, checks RAW/WAR/WAW dependencies, and writes MemInterfaceAttr for dependent ports. The loop_array load/store already satisfy those conditions.

/home/meetb/wave6cc/dynamatic-zenodo-exact/lib/Dialect/Handshake/MemoryInterfaces.cpp:104-108,188-209

The interface builder creates an LSQ when LSQ inputs exist and derives each group size from the grouped LSQ ports. This is the source of the observed group [2].

The exact pass precondition also holds: HandshakeSpeculationV2.cpp:806-809 requires one FuncOp; the specimen has one. HandshakeSpeculationV2.cpp:822-827 seeds frontiers only for the configured loop BB; the run metadata selects actual BB 1.

## 7. Strongest-representation audit

The combined case includes all ordinary existing metadata relevant to this question:

- LSQ group id: LSQ: 0.
- LSQ group size: [2].
- Load/store group membership: load0 and store0.
- Load/store ordering dependencies: reciprocal handshake.deps.
- Address dependencies: load address and store address are connected to LSQ-produced channels.
- Data dependency: load data flows through the arithmetic update into store data.
- Allocation/control information: LSQ control inputs/outputs and loop group control are present.
- Memory interface metadata: both operations are explicitly mem_interface<LSQ: 0>.
- Speculation/eager control: spec_v2_repeating_init, forked control, and passer frontier wiring.
- Branch/control dependence: all memory operations carry handshake.bb = 1; the speculative frontier is selected for BB 1.
- Exact pass preconditions: single function, valid block mapping, complete materialized Handshake IR.

No ordinary metadata was added to make the composition succeed. The already-produced strongest representation succeeds. This is not a missing-information artifact.

## 8. Minimized reproducer

The existing loop_array fixture is already the smallest useful source-backed reproducer found in this checkout:

~~~~c
for (int i = 1; i < n; i++)
  c[i] = k + c[i - 1];
~~~~

It has one loop/control decision, one load, one store, one LSQ, one memory region, and one necessary loop-carried dependence.

The three outcomes are:

- LSQ-only: successful LSQ instantiation and interface assignment.
- eager-only: successful SpeculationV2 rewrite on the golden-ratio control case.
- LSQ plus eager: successful composition on loop_array, retaining the LSQ-backed load while applying eager/speculative control rewriting.

## 9. Independent semantic oracle

Oracle source:
/home/meetb/wave6cc/wave6cc-semantic-oracle.py

Oracle output:
/home/meetb/wave6cc/wave6cc-semantic-oracle.md

The oracle is an independent finite-state exhaustive event-permutation model. It does not implement a compiler pass. It models LSQ allocation, address resolution, ordered store/load validation, speculative branch commit, and architectural commit.

~~~~text
| Case | EAGER_VALID? | LSQ_VALID? | COMBINED_SEMANTICALLY_VALID? | CURRENT_COMPILER_ALLOWS_COMPOSITION? |
|---|---:|---:|---:|---:|
| known-address, no-alias load | YES | YES | YES | YES |
| unresolved-address load | NO | YES | YES | YES |
| potentially aliasing load | YES | YES | YES | YES |
| load-only LSQ traffic | YES | YES | YES | YES |
| load with older store | YES | YES | YES | YES |
| one iteration | YES | YES | YES | YES |
| overlapping iterations | YES | YES | YES | YES |
~~~~

For unresolved addresses, immediate eager data production is invalid, but LSQ allocation followed by waiting for address resolution is valid; the combined semantics remain valid. For potential aliasing and older stores, speculative issue is followed by ordered validation/replay or forwarding before architectural commit. The actual compiled loop_array specimen confirms that the current compiler accepts the represented composition.

## 10. Counterexample matrix

The oracle found no semantic counterexample to LSQ plus eager composition in the required cases:

| Case | Semantic result | Compiler result |
|---|---|---|
| Known address, no alias | valid | composed |
| Unresolved address | wait, then valid | represented structurally |
| Potential alias | validate/replay or order, valid | composed |
| Load-only LSQ traffic | valid | composed |
| Load with older store | order/forward, valid | composed |
| One iteration | valid | composed |
| Overlapping iterations | ordered per LSQ age/group, valid | composed |

## 11. Exact files and command outputs

LSQ-only and combined IR:

- /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/clang.ll
- /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/translated.mlir
- /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/cf.mlir
- /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_before_lsq.mlir
- /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_after_lsq.mlir
- /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_transformed.mlir
- /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_pre_speculation.mlir
- /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_speculation.mlir
- /home/meetb/wave6cc/wave6cc-phase-d-loop-array/comp/handshake_post_speculation.mlir

Eager-only IR:

- /home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/handshake_pre_speculation.mlir
- /home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/handshake_speculation.mlir
- /home/meetb/wave6cc/wave6cc-phase-c-eager-golden-ratio/comp/handshake_post_speculation.mlir

All required experimental compiler stages completed successfully with exit code 0. No source patch, IR stub, licensed simulator, FPGA20 placement, or Gurobi-dependent target was used.

TERMINAL_CLASSIFICATION = EXISTING COMPOSITION SUFFICES
