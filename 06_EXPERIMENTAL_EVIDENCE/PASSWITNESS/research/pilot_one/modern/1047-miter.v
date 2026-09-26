module passwitness_miter(
    input [2:0] w,
    output mismatch,
    output reference_y,
    output candidate_y
);
    golden gold(.w(w), .y(reference_y));
    candidate cand(.w(w), .y(candidate_y));
    assign mismatch = reference_y ^ candidate_y;
endmodule
