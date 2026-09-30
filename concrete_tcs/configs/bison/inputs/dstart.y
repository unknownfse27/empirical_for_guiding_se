%start S
%start X
%token A
%%
S: A;
X: A A;
