%glr-parser
%expect-rr 3
%%
s: a|b;
a: %expect-rr 3;
b: %expect-rr 3;
