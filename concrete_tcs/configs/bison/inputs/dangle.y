%token IF ELSE THEN ID
%%
s: IF c THEN s | IF c THEN s ELSE s | ID;
c: ID;
