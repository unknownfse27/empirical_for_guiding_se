%token IF THEN ELSE ID
%%
s:IF e THEN s|IF e THEN s ELSE s|ID;e:ID;
