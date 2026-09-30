%define api.pure
%define parse.error verbose
%define api.prefix {p}
%token-table
%token A
%%
S:A;
