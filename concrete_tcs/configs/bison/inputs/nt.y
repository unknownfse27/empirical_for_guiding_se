%union{int x; float y;}
%nterm <x> S
%nterm <y> E
%type <x> A
%token <y> B
%%
S: E; E: A B { $$ = $1; }; A: %empty;
