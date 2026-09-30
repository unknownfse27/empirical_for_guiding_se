%token A "$" B "@" C "[" D "]" E "??!" F "??/" G "??<"
%define api.prefix {a$@[]}
%%
s:A|B|C|D|E|F|G;
