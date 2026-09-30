%token A B C D
%%
start: e | f;
e: A B | A B C;
f: A B | D B;
