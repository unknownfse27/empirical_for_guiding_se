%glr-parser
%token A B
%type <int> x
%start S1
%start S2
%%
S1: x;
S2: x;
x: A %expect 0 %expect-rr 0 %dprec 1 %merge<m> {$$=1;} B {$$=$<int>1;} | %?{1} A %dprec 2 %merge<m> | %empty ;
