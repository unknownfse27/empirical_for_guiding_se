%union{int i;}%token <i> A B
%type <i> e
%%
e: A { $$=$<i>2; @$=@2; } B | A B { $$=$<i>0+$<i>-1; @$=@$; };