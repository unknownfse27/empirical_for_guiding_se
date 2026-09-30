%token A B C
%%
s:s s|s A|s B|s C|A|B|C;
