module tb(output pre_y, output post_y);
    reg [2:0] w;
    pre pre_instance(.w(w), .y(pre_y));
    post post_instance(.w(w), .y(post_y));
    initial begin
        w = 3'b100;
    end
endmodule
