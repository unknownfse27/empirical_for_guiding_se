%token a b c d
%%
S:A a|b A c|B c|b B a;
A:d;
B:d;
