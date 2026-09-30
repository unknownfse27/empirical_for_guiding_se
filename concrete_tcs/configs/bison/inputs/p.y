/*c*/
%{
int x;
%}
%locations
%define parse.error verbose
%name-prefix"zz_"
%union{int n;double d;}
%token<n>N <d>D
%nterm<n>e
%destructor{}<*>
%left"+"
%%
e:N|D{$$=0;}|e"+"e|error;
