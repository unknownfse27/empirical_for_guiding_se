%locations
%left"+""*"
%token N
%type<int>e
%%
e:e"+"e%prec"*"{$$=$1+$3;}|e"*"e{$$=$1*$3;}|N|{int x=1;}e{$$=$2+x;};n:N;
