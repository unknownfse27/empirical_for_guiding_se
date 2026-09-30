%printer { print($$); } <*>
%destructor { free($$); } <>
%token A "'\x0a'" B "'\u1234'" C "'\U00001234'" D "'\123'" E ""\n\t\r""
%%
s: A B C D E;
