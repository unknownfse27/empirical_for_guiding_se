%token <int> NUM
%left "+" "-"
%left "*" "/"
%right "^"
%nonassoc UMINUS
%%
e: e "+" e|e "-" e|e "*" e|e "/" e|e "^" e|"-" e %prec UMINUS|"(" e ")"|NUM;
