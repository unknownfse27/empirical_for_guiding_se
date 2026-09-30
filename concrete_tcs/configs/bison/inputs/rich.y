%lex-param {int x}
%parse-param {int y}
%printer { } <*>
%binary "<="
%default-prec
%initial-action{}
%token-table
%%
start[r]: "a"[n] { $r=1; @r=@n; YYERROR; } | "c"{}"d"{$$=$2;} | %empty { $r=0; };
