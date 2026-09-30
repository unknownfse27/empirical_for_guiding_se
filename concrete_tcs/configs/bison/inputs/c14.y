%glr-parser%expect-rr 1%token A
%%
S:X|Y;
X:A%dprec 1;
Y:A%dprec 2;
S:Z;
Z:A%merge<stmtMerge>;
