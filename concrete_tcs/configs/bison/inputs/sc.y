%code top{int a;}
%code requires{int b;}
%token<int> NUM[N] "n" 97
%type<int> e[r]
%left "+" "-"
%define api.namespace {N}
%%
e[r]:NUM[n] {$r=$n;}|e "+" e {$r=$1+$3;};
