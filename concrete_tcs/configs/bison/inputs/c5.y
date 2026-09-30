%language"c++"
%define parse.assert
%define api.token.constructor
%define api.value.type variant
%define api.parser.class{P}
%define api.namespace{N}
%locations
%token<int>N
%nterm<int>e
%%
e:N|e N{$$=$1+$2;};
