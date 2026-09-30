%{int x;%}
%token <int> A
%destructor { free($$); } A
%printer { fprintf(yyoutput,"v",$$); } A
%nterm <int> s
%%
s: A { $$ = $1; };
%%
int yylex(){return 0;}
