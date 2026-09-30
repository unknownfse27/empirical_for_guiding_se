%union{int n;}
%nterm<n>a
%token<n>A B
%token A
%token A 65
%nondeterministic-parser
%default-prec
%yacc
%left A
%right A
%destructor{}A
%destructor{}A
%nterm error
%%
a:A;d:B %prec A %prec A;
f T;