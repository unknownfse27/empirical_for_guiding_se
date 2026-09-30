%glr-parser
%token WORD
%%
s:w;w:WORD|w WORD|w w;
%%
