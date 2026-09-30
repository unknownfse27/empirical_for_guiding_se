%token N
%left "+" "-"
%left "*" "/"
%right "^"
%nonassoc "<" ">"
%precedence NEG
%%
e: N | e "+" e | e "*" e | e "^" e | e "<" e | "-" e %prec NEG;
