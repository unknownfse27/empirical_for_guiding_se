%parse-param {int *r}
%lex-param {void *s}
%union {int i;}
%token <i> N
%nterm <i> e
%destructor {} <i>
%left '+'
%%
e: e '+' N | N ;