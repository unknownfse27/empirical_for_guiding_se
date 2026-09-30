%token N
%type <int> e
%locations
%%
e: N { $$=$1+$-1+$<int>1; @$=@0; } | e[left] e[right] { $$=$left+$right; @$.first_line=@1.first_line; } ;
