%union {int i; char *s;}
%token <i> NUM
%type <i> e
%%
e: NUM {$<i>$=$<i>1;} | e NUM {$<i>$=$<i>1+$<i>2;} ;