%glr-parser
%token A B
%expect-rr 2
%%
s:e|f|f;
e:A;
f:A;
