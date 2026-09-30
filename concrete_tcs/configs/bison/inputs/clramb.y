%define lr.type canonical-lr
%token A B C D E
%left A
%%
s: s A s | s B s | s C | D | E ;