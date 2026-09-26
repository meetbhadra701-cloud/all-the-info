#!/usr/bin/env bash
# P0: runs MappingEvolve's exact compress2 preprocessing (the command string copied from main.cpp abc_compress2)
# once per benchmark, so that every mapper starts from the identical AIG.
set -u
M=/w/third_party/MappingEvolve/third-party/mockturtle/experiments/benchmarks
O=/w/experiments/inputs/c1/c2; mkdir -p $O
S=/w/experiments/results/c1_p0_preprocess.csv; echo "bench,orig_md5,c2_md5,orig_stats,c2_stats" > $S
EPFL="adder bar div hyp log2 max multiplier sin sqrt square arbiter cavlc ctrl dec i2c int2float mem_ctrl priority router voter"
ISCAS="c17 c432 c499 c880 c1355 c1908 c2670 c3540 c5315 c6288 c7552"
IWLS="ac97_ctrl aes_core des_area des_perf DMA DSP ethernet iwls05_i2c leon2 leon3_opt leon3 leon3mp iwls05_mem_ctrl netcard pci_bridge32 RISC sasc simple_spi spi ss_pcm systemcaes systemcdes tv80 usb_funct usb_phy vga_lcd wb_conmax"
for b in $EPFL $ISCAS $IWLS; do
  yosys-abc -q "read_aiger $M/$b.aig; balance -l; rewrite -l; refactor -l; balance -l; rewrite -l; rewrite -z -l; balance -l; refactor -z -l; rewrite -z -l; balance -l; write_aiger $O/$b.aig" > /dev/null 2>&1
  s0=$(yosys-abc -q "read_aiger $M/$b.aig; print_stats" 2>&1 | grep -o "i/o = *[0-9]*/ *[0-9]*.*and = *[0-9]*.*lev = *[0-9]*" | tr -s ' ' | tr ',' ';')
  s1=$(yosys-abc -q "read_aiger $O/$b.aig; print_stats" 2>&1 | grep -o "i/o = *[0-9]*/ *[0-9]*.*and = *[0-9]*.*lev = *[0-9]*" | tr -s ' ' | tr ',' ';')
  echo "$b,$(md5sum < $M/$b.aig | cut -c1-32),$(md5sum < $O/$b.aig | cut -c1-32),$s0,$s1" >> $S
done
cat $S
