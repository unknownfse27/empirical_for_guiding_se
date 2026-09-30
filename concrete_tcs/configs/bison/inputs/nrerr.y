%token A
%%
s:A {$$=$[no.such]; @$=@nope;};
