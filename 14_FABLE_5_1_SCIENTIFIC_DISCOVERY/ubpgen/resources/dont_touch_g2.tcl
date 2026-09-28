# POST_SYNTH hook (Gate 2): the via sites and line taps are part of the FIXED base -- never resize, remove or buffer-swap them
set cnt 0
foreach inst [[ord::get_db_block] getInsts] {
  set m [[$inst getMaster] getName]
  if {[string match VSITE_* $m] || $m eq "LTAP"} { $inst setDoNotTouch 1; incr cnt }
}
puts "G2: dont_touch set on $cnt via-site/line-tap instances"
