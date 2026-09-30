%locations
%parse-param{int*p}
%lex-param{int*p}
%union{int n;}
%token<n>N
%type<n>e
%%
e[x]:N[y]{$x=$y;}|e[x] N[y]{$x=$x+$y;};
%%
