%define lr.type ielr
%token A B C
%%
s:a|b;a:A B|A C;b:A B|A C;
%%
