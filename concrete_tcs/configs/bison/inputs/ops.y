%left A
%right A
%nonassoc "="
%left "+"
%right "*"
%precedence NEG
%token ATOKN
%%
start: e;
e: e "=" e | e "+" e | e "*" e | ATOKEN | "a" | 'x';
