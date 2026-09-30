%defines
%locations
%union{int n;}
%token <n> NUM
%left "+"
%%
expr:NUM|expr "+" expr;
