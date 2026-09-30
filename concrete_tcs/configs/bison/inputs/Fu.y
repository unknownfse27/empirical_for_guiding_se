%define parse.error verbose
%define api.pure
%define api.prefix {x}
%no-lines
%output "y.tab.c"
%file-prefix "y"
%token-table
%expect-rr 0
%no-default-prec
%no-lines
%token N
%%
e:N;
