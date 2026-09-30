%token EOF 0 "end of file" A 256 "A" B 257 "B"
%define api.prefix {x_}%no-lines%locations
%%
S:A B|error EOF;
