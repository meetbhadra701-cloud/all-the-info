"""Reusable research harness: architecture-free infrastructure proven in the UBP project.

Every module here is a decoupled copy of a component that produced validated results in
`14_FABLE_5_1_SCIENTIFIC_DISCOVERY/ubpgen/` (commit b14195a). The originals are untouched, so historical
reproducibility is unaffected. `tests/test_harness.py` checks that each copy behaves like its original.

  records   configuration hashing, provenance, append-only JSONL records
  decision  pre-registered comparative decision rules (candidate vs the strongest competitor)
  oracle    independent-oracle + mutation-control wrapper; AIGER reader and cycle simulator
  sky130    pinned SKY130 corner libraries (download once, sha256-verified)
  liberty   minimal Liberty reader / editor (areas, pin caps, NLDM tables, safe attribute edits)
  sta       OpenRCX extraction + one-corner OpenSTA session templates, and their report parsers
  accounting  flattened-netlist vs final-DEF accounting of what a physical flow added or resized
  orfs      OpenROAD-flow-scripts runner (docker), stage metrics, DRT / GRT log parsers

See ../README.md for the stage interface these pieces plug into.
"""
__version__ = '0.1.0'
