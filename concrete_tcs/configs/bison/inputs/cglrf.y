%language "c++"
%glr-parser
%locations
%define api.value.type variant
%define api.value.automove
%define api.token.constructor true
%token <int> N
%type <int> E
%left "+"
%%
E: N { $$=$1; } | E "+" E { $$=$1+$3; };
