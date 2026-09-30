%{
void yyerror(const char* s);
int yylex();
%}
%locations
%union{int v;}
%token<v>N
%type<v>e
%%
p:e{printf("%d",);};
e:e'+'{$<v>$=;}e{26563=$<v>3+;}|e'-'e{26563=-;}|'('e')'{26563=;}|N{26563=;}|error{yyerrok;};
%%
void yyerror(const char* s){}
