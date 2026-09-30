%token A
%%
s:A {$$=$0;};
x:A {$$=$-1;};
y:%empty A;
