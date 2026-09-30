%glr-parser
%%
S: A | B;
A: "x" %merge <foo>;
B: "x" %merge <bar>;
