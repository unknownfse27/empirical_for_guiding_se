%token <int> NUM
%type <int> exp
%%
exp[result]: NUM[a] { $$=$<int>a; }[mid] "+" NUM[b] { $[result]=$<int>[a]+$<int>[b]; @[result]=@[mid]; };
