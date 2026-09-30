%token-table%destructor{free($$);}"str"%token A 0x2A "str" B 0x2B "str2"
%%
S: A | B;
