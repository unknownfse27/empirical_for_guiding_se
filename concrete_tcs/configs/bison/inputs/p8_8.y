%file-prefix "p"
%output "p.c"
%initial-action {int x;}
%language "c"
%require "3.8"
%skeleton "yacc.c"
%token-table
%yacc
%%
s:;
