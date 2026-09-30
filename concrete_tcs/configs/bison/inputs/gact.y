%glr-parser
%union {int i;}
%token <i> A B
%type <i> e
%%
e: A {$$=$1;} | B {$$=$1;} | A B {$$=$1+$2;} | e e {$$=$1+$2;} ;