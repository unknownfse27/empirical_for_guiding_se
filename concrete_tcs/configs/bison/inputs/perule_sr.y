%token IF THEN ELSE
%%
s: IF s THEN s %expect 1 | IF s THEN s ELSE s | IF;
