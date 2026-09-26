# 07 — Prior-art prosecution (Wave 14 increment)

**Base document:** `13_FABLE_5_1_SCIENTIFIC_DISCOVERY/04_STRONGEST_PRIOR_ART.md` (HIST-OBS). It is not repeated here.

**New this session:**
- the search log `evidence/prior_art_search_2026-09-26.md`;
- one competitor family the archive never considered (§3);
- an explicit obviousness verdict (§4).

**Access:**
- Full texts are still unreadable here: arxiv, ACM, IEEE, substack and yongwei.site are blocked.
- Every paper claim below is a search-engine **[summary]**.

## 1. The claim under prosecution

In a metal/via-programmable fabric (regime V), each block of g inputs gets a **weight-independent** generator of all canonical signed subset sums. The generator's pattern lines, and their shared negations, are **shared by every neuron** (and every matrix fed by the same activations). Each neuron's leaf picks one line, its negation, or zero **with a via**: no index storage, no mux. Each neuron's tree then has ⌈n/g⌉ leaves instead of n.

Variants:
- **H1.1:** bit-parallel.
- **H1.2:** bit-serial. Pattern lines are single wires, and generators and trees are serial adders.

## 2. Element-by-element anticipation

| Claim element | Closest reference | Anticipated? |
|---|---|---|
| (a) All signed subset sums of g activations precomputed once, symmetric half + sign | TENET 2509.13765: "mirror-half pre-compute adder logic … shared pre-compute table", "2-bit dense index … 1-bit sign index". Also T-MAC and LUT Tensor Core (symmetry halves the table). | **Yes** (runtime) |
| (b) Shared across all output neurons | TENET ("TLUT PEs that share the precompute logic and table"); LUT Tensor Core (elongated tiling for table reuse) | **Yes** (runtime) |
| (c) Selection fixed at fabrication by via/metal, with base layers weight-independent | HNLPU (M8–M11 only); Taalas HC1 (two metal masks; "via-selectable bitline"); Ankhdjet (via-mask program) | **Yes** as a fabric concept. In every retrieved summary it is applied at g = 1 (per input, or per weight value). |
| (d) The combination (a)+(b)+(c): *multi-input* universal patterns selected by via | — | **Not found** in any retrieved summary |
| (e) Bit-serial pattern streams feeding serial/popcount neurons | HNLPU (bit-serial POPCNT neurons fed by raw inputs) | Style anticipated; pattern-stream feeding not found |
| (f) Port-bound optimality (Theorem 1, previous session) | — | Not found |

**New this session:**
- **TOM (2602.20662)** synthesizes ternary ROM weights as standard-cell logic, with "conditional negation" plus a shared adder tree. That is again g = 1.
- **The Taalas "LUT scheme" as decoded by Zhao** pre-multiplies each activation by *all weight values* and selects through a ROM plus a one-hot decoder. That is sharing across weight values (g = 1 over inputs), with a decoder/select rather than a bare via.

## 3. A competitor family the archive never considered: ROM-based distributed arithmetic (DA)

- **Classical DA** (Peled & Liu 1974; White 1989) is the *transpose* of UBP:
  - It stores, per output row and per block of K inputs, the 2^K sums of **weight** subsets.
  - Each cycle, it indexes that table with the K current **input bits** (bit-serial inputs).
- **A DA table is a ROM.** Its content depends on W, but its structure does not: word-line decoders are shared by all rows, and the bit cells are via-programmed. **DA is therefore regime-V compatible when built as a via-ROM macro.** Taalas's 1T via-ROM shows such macros are production practice.
- **Cost structure** (ternary W, bit-serial INT8 x; NEW-INF, not measured):
  - **DA per row:** 2^K ROM bits per block per bit of block-sum width, plus a multi-bit adder tree over n/K block values, plus a shift-accumulator.
  - **UBP-serial per row:** n/K single-bit serial leaves, with no per-row storage.
  - **Which wins** depends on the ROM bit area relative to a serial-adder node. At advanced nodes a 1T via-ROM bit is roughly two orders of magnitude smaller than a flip-flop-based serial adder. **DA-as-via-ROM may therefore be a stronger regime-V baseline than g1_V.**
- **Why E5/E6 cannot test it:**
  - A via-ROM is a transistor-level array. Standard-cell PnR (our evaluator) would realize the table as weight-specific logic, which is regime F (this is what TOM does). That is not a fair model of a ROM macro.
  - This is recorded as the **largest open baseline gap** (13_FINAL_META_REVIEW Q3/Q7).

## 4. Obviousness verdict

- **What an examiner has:**
  - Element sets (a)+(b) are published by the LUT-accelerator family.
  - Element (c) is published by the hardwired-silicon family.
  - Joining them is a combination of known elements, and the logic saving is predictable. The "no mux, the index is a via" step is what a skilled designer would do on learning that weights are constant.
- **Verdict:** the mechanism is **likely obvious** in the patent sense, even if no reference shows the combination. It is **not a strong novelty claim.**
- **What remains contributable (scientific, not patent):**
  1. **The cost structure of the combination.** Removing the mux moves the cost into select wiring: (3^g − 1)/2 candidate lines per block must reach every site. Whether the logic saving survives that wiring is unknown and non-obvious in outcome, even if obvious to try. **E5/E6 measure exactly this.**
  2. **The price of universality** vs weight-specific CSE (previous session: in regime F, hashing captures most of it).
  3. **Port-bound optimality** (Theorem 1).
- **Consequence for the thesis:**
  - It is framed as a **characterization** of when universal block sharing pays in via-programmable silicon, not as an invention.
  - Success condition: a physical routed-area advantage ≥ 1.5× (E5/E6).

## 5. What would change this verdict

- **HNLPU full text** (★) showing shared pre-summed multi-input streams: the combination would be anticipated. A physical characterization of it would then be less new.
- **Taalas HC2 disclosures or patents** describing multi-input pattern sharing: the same consequence.
- **A DA-via-ROM comparison showing DA dominates UBP in regime V:** the thesis would lose its practical relevance even if physically valid. This needs a transistor-level ROM model, which is out of scope here.
