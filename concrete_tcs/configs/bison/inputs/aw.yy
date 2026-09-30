%skeleton "lalr1.cc"
%define api.value.automove
%token <int> NUMBER "number" TWICE "twice" THRICE "thrice"
%type <int> exp
%%
exp:"number"{$$=$1;}|"twice" exp{$$=$2+$2;}|"thrice" exp[v]{$$=$2+$v+$2;};
