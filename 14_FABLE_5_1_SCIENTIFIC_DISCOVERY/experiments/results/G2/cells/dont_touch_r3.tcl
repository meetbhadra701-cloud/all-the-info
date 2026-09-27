# POST_SYNTH hook (R3): via sites and line taps (LTAP, LTAP2) are part of the FIXED base
set cnt 0
foreach inst [[ord::get_db_block] getInsts] {
  set m [[$inst getMaster] getName]
  if {[string match VSITE_* $m] || [string match LTAP* $m]} { $inst setDoNotTouch 1; incr cnt }
}
puts "G2/R3: dont_touch set on $cnt via-site/line-tap instances"
