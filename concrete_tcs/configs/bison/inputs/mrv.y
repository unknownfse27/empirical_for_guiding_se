%union {int i;}
%token <i> NUM
%type <i> e
%%
e: {$$=0;} NUM {$$=$<i>2;} | NUM {$$=$1;} ;