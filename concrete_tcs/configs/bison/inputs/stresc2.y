%token A "\""
%token B "back\\slash"
%token C "null\000byte"
%%
s: A | B | C ;