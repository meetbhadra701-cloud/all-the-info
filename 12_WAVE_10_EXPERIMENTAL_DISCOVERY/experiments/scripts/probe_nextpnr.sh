#!/usr/bin/env bash
# Screening probe for C3: which nextpnr builds and FPGA chip databases the local OSS CAD Suite has (read-only listing, nothing executed)
OSS=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
ls $OSS/bin | grep -i "nextpnr\|icepack\|ecppack\|gowin\|apycula\|prjoxide\|vpr\|openfpga" | tr '\n' ' '; echo
ls $OSS/share 2>/dev/null | tr '\n' ' '; echo
ls $OSS/share/nextpnr 2>/dev/null | head; du -sh $OSS/share/nextpnr/* 2>/dev/null | head
file $OSS/libexec/nextpnr-ecp5 2>/dev/null || file $OSS/bin/nextpnr-ecp5
cat $OSS/VERSION 2>/dev/null; ls $OSS/examples 2>/dev/null | head
