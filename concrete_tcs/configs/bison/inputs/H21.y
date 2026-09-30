%glr-parser
%expect-rr 10
%token N P S
%left P
%left S
%%
e: e e | e P e | e S e | N | ;
