%nonassoc '<' '>' EQ
%precedence UMINUS
%left '+' '-'
%left '*' '/'
%right '^'
%token NUM EQ
%%
expr: expr '<' expr | '-' expr %prec UMINUS | expr '+' expr | expr '*' expr | expr '^' expr | NUM ;
