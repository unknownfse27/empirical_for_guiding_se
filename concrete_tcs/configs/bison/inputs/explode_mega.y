%glr-parser
%expect-rr 10
%expect 10
%token A B C
%left A
%right B
%%
s: e | s s | s A s | s B s;
e: A | B | C | %empty;
