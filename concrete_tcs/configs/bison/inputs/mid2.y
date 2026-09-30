%token A B
%type <int> X Y Z W
%%
x: A {$<int>$=1;} B {$<int>$=$<int>1+1;} {$<int>$+=$<int>2;} ;
X: A;
Y: A;
Z: A;
W: A;
