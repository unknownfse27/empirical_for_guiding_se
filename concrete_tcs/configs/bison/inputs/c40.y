%token EOF 0 "eof" A 256 "a" B 257 "b"%define api.token.prefix {TOK_}%locations%define parse.lac full
%%
S:A B|error EOF;
