# 15 — Gate 1: exact novelty and obviousness prosecution

## The claim prosecuted (verbatim scope)

> A weight-independent base-layer hardware fabric for binary/ternary MVM that computes shared block-pattern sums once, shares them across output neurons, and programs neuron-specific selection through top-metal/via connectivity, so the expensive lower layers remain unchanged across weight matrices.

## Evidence base and access (read before trusting any row)

| Source | Access | Status |
|---|---|---|
| **Ankhdjet** 0.1.0 (compiler + RTL + reference models + silicon calibration) | **Primary source.** PyPI wheel `ankhdjet-0.1.0-py3-none-any.whl`, sha256 `a3d2abec…231d9d1a`. Unpacked and **read, not executed**. Files: `_rtl/column/cirom_nor_tile.sv`, `reference/{mac,nor}.py`, `_pdk/sky130/estimators/sky130_v4.yaml`. | READ |
| HNLPU (ASPLOS'26, arXiv 2508.16151) | arxiv, ACM, alphaXiv, yongwei.site and emergentmind are **all blocked** by the egress proxy | search summaries only |
| Taalas HC1 | Product press, plus the HNLPU author's "HC1 decoded" (blocked) | summaries only |
| WO2025217724A1 (mask-programmable ROM, shared drain bit lines) | Google Patents blocked | summary only; **applicant not visible** |
| BitROM, TOM, T-MAC, LUT Tensor Core, TENET, 2604.25183, TLMAC (FPGA'24), YOLoC, CSHM / alphabet-set multipliers | arxiv/ACM/IEEE blocked | summaries only |

Everything except Ankhdjet is **secondary**. No novelty is inferred from missing wording.

## Per-method analysis (the eight questions)

**Key:**
- **W** = where the weights physically reside.
- **Base W-indep?** = are the lower layers weight-independent?
- **Shares act-group sums across outputs?**
- **All patterns?** = all patterns generated, or only weight-specific ones.
- **Selection** = how selection is done.
- **Reusable base?** = physically reusable across W without new lower masks.
- **Δ vs UBP** = the exact difference.
- **Obvious?** = would a competent combiner reach UBP?

| Method | W | Base W-indep? | Shares act-group sums across outputs? | All patterns? | Selection | Reusable base? | Δ vs UBP | Obvious? |
|---|---|---|---|---|---|---|---|---|
| **Ankhdjet** (primary source) | 1 NMOS per ternary weight. The drain is via-routed to BL+ / BL− / GND ("each cell's via/jog choice is the entire per-model mask difference") | **Yes** (fixed macro; via mask only) | **No.** One-hot WL reads one input row per cycle. Per output column: `acc += (pos_hit − neg_hit)·act_bit << k` over N rows × K bit-slices. **g = 1.** | n/a (per-weight storage) | Via on the cell drain (ROM storage) | **Yes** | Per-weight storage, time-multiplexed (T ≈ K·SUBCOL_ROWS = 512 cycles/dot at 64-row sub-columns). No cross-output activation sharing. | — |
| **HNLPU** "Sea-of-Neurons" (summary) | Metal routing in M8–M11 of a **pre-fabricated generic neuron array ("structured ASIC")**. 60/70 masks shared. | **Yes** | **Not per summaries.** Inputs are routed into 16 value regions *per neuron*, with POPCNT on bit-serial inputs: the distributive law **within** a neuron. | n/a | Metal routing of each input to a region | **Yes** | Groups by **weight value within a neuron**. UBP groups **inputs across neurons**. | ✔ as a host fabric |
| **Taalas HC1** (third-party decode) | Mask ROM, 2 metal masks | Yes | Pre-multiplies each activation by **all weight values** (per input), shared; a ROM + one-hot decoder selects | All *values* of one input (g = 1) | ROM + decoder (a runtime select) | Yes | g = 1 over inputs. The selection is ROM-decoded, not a bare via. | ✔ |
| **WO2025217724A1** (summary) | 1 transistor per weight. Several bit lines coupled by mask-programmable vias. | Yes | No (a storage cell) | n/a | Via to the chosen BL | Yes | Storage primitive, not an arithmetic fabric | — |
| **BitROM / TOM / YOLoC / Hidden-ROM** (summaries) | ROM cells. TOM synthesizes ternary ROM as logic. | Partly (TOM: logic is W-specific) | No. Per-weight add/sub/skip or bitline accumulation. | n/a | ROM read / logic | ROM: yes; TOM: no | Per-weight accumulation | — |
| **T-MAC / LUT Tensor Core / TeLLMe / 2604.25183** (summaries) | Memory (runtime indices) | Yes (programmable chip) | **Yes.** A table of activation-group partial sums is precomputed once and shared/reused. | **All** 2^g or 3^g/2 (mirror-half) | **Runtime mux / table read, indexed by stored weight codes** | Yes (software-programmable) | The index is a runtime value (storage + mux per lookup). UBP: the index is a fabrication-time via, with no mux and no index memory. | ✔ as the arithmetic |
| **TENET** (summary) | Memory | Yes | **Yes.** "TLUT PEs share the precompute logic and table", with mirror-half precompute and a sign index. | All (mirror-half) | Runtime index (2-bit dense + 1-bit sign) | Yes | Same arithmetic as UBP; runtime select | ✔ |
| **TLMAC** (FPGA'24, summary) | FPGA LUT truth tables (configuration bits) | Yes (FPGA silicon) | Shares **weight-group** tables (DA-style: LUT inputs = activation bits) across outputs with the same weight group. A "LUT pool" plus switches select per output. | **Only W-specific** (the unique weight groups present) | Programmable routing switches (FPGA config) | Yes (reconfigure) | Shares **weight-side** tables, only for groups present. UBP shares **activation-side** sums of **all** patterns. | ◐ |
| **CSHM / alphabet-set multiplier** (Park, Muhammad, Roy, ~2002–04, summary) | Coefficient-specific select control | Precomputer is W-independent | **Yes**, at g = 1: all odd multiples {1,3,…,15}·x are precomputed and shared across all coefficient multipliers | **All values of one input** | Shift + mux per coefficient | — | Universal precompute + per-constant select is **decades-old at g = 1** | ✔ (principle) |
| **Distributed arithmetic** (Peled–Liu 1974; White 1989) | ROM of **weight** subset sums per output | ROM array W-independent; contents via-programmable | **No.** It shares the *address* (input bits) across outputs, but tables are per output. | All 2^K input patterns per output (W-specific contents) | ROM read indexed by input bits | Yes (via-ROM) | The transpose of UBP. See Gate 3: it is a competitor, not an anticipation. | — |
| **Four Russians / Lupanov** | math | — | Precompute all subset sums of column blocks, shared across rows | All | Table lookup (software) | — | The mathematical core; no hardware or programmability claim | ✔ (math) |
| **Structured ASIC / via-configurable gate arrays** (generic) | Via/metal configuration of generic cells | Yes | Any W-specific CSE circuit could be mapped onto it | W-specific | Via-configured logic | Yes | A generic host that could implement **W-specific** sharing (CSE) at structured-ASIC density cost. It is not universal-pattern sharing. | ◐ as a competitor |

## Classification

- **Identical mechanism:** **none found** in any retrieved source. That includes the one primary source (Ankhdjet), whose RTL shows g = 1 per-weight accumulation.
- **Technically equivalent mechanism:** **none found.** TENET/T-MAC are arithmetically equivalent but use runtime-indexed selection (storage + mux). That changes the physical cost structure, so they are not technically equivalent as hardware.
- **Obvious composition of known methods: YES, likely.** Every element exists:
  - (a) Universal activation-group precompute shared across outputs: T-MAC / LUT Tensor Core / TENET, including mirror-half symmetry.
  - (b) Universal precompute plus fixed per-constant selection at g = 1: CSHM, Taalas-decoded.
  - (c) A W-independent base array programmed only in top metal/vias: HNLPU Sea-of-Neurons, explicitly a "structured ASIC"; Taalas; Ankhdjet.
  - A competent designer who knows (a) and (c) would try "hardwire the LUT index", and would generate **all** patterns because the base cannot know W. The step is predictable in *logic* (≈ g× fewer adders).
- **Nontrivial architectural contribution: only in the physical consequences.** Their size and even sign are not predictable from the references:
  - bit-parallel UBP loses a utilization step to select-bus congestion (E5);
  - bit-serial UBP routes like the baseline with 5.8× less programmable wire (E6);
  - UBP meets Theorem 1 (port bound) with equality.
  
  **None of these physical results appears in any retrieved source.** They are the only candidate contribution. By Gate 3's evidence they may be outweighed by stronger competitors.

## Gate-1 verdict: **MATERIALLY DOWNGRADED, not killed**

- **Kill-condition check:**
  - "A prior method already substantially implements the same fabric": **not found.** This is provisional because HNLPU's full text is unread.
  - "Routine combination whose physical consequences are already established": the combination is routine, **but its physical consequences are not established in any retrieved source.**
- **Downgrade.** UBP can no longer be presented as an invention. It is an **obvious composition** whose publishable content, if any, is:
  - (i) the physical characterization under W-independence;
  - (ii) the port-bound optimality;
  - (iii) whatever Gate 3 leaves standing on competitiveness.

## Evidence still missing (exactly)

1. **HNLPU full text.** Whether "Sea-of-Neurons" neurons consume shared pre-summed multi-input streams, and how value regions are sized W-independently. Blocked: arxiv, ACM, alphaXiv, yongwei.site.
2. **Taalas disclosures.** Whether the WO2025217724A1 applicant is Taalas, and whether HC2 uses multi-input patterns. Google Patents blocked.
3. **TENET / T-MAC full texts.** Whether either discusses a hardwired or constant-index variant. Blocked.
4. **The Ankhdjet repository-side physical flow** (custom cells, LibreLane). Not in the wheel. `github.com/mpai17/ankhdjet` was not attached to this session.
