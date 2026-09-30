%token A "hello\tworld"
%token B "foo\nbar"
%token C "a\rb"
%%
s: A | B | C ;