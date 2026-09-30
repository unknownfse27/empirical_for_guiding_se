%token A
%parse-param { int *x } { char *y }
%lex-param { int *x }
%initial-action { yy = 0; }
%locations
%%
s: A;
