module top(input [319:0] x, output [14:0] y);
  wire signed [14:0] s = $signed(x[9:0]) + $signed(x[19:10]) + $signed(x[29:20]) + $signed(x[39:30]) + $signed(x[49:40]) + $signed(x[59:50]) + $signed(x[69:60]) + $signed(x[79:70]) + $signed(x[89:80]) + $signed(x[99:90]) + $signed(x[109:100]) + $signed(x[119:110]) + $signed(x[129:120]) + $signed(x[139:130]) + $signed(x[149:140]) + $signed(x[159:150]) + $signed(x[169:160]) + $signed(x[179:170]) + $signed(x[189:180]) + $signed(x[199:190]) + $signed(x[209:200]) + $signed(x[219:210]) + $signed(x[229:220]) + $signed(x[239:230]) + $signed(x[249:240]) + $signed(x[259:250]) + $signed(x[269:260]) + $signed(x[279:270]) + $signed(x[289:280]) + $signed(x[299:290]) + $signed(x[309:300]) + $signed(x[319:310]);
  assign y = s;
endmodule
