%token A 65
%token B 65
%left A
%file-prefix "o1"
%file-prefix "o2"
%%
start: A;
A: "x";
: "y";
