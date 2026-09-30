%file-prefix "x"
%no-default-prec
%no-lines
%output "/tmp/x\a\b\f\n\r\t\v\x41\042y.c"
%token-table
%expect-rr 0
%error-verbose
%pure-parser
%name-prefix "p"
%verbose
%token N
#line 9 "f"
%%
s:N;
