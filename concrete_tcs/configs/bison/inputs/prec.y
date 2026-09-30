%define lr.type lalr
%expect 1
%token NUM PLUS
%left PLUS
%%
e: e PLUS e | NUM;
