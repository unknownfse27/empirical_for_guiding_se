%language "Java"
%define package "pkg"
%define api.parser.class { P }
%define api.parser.public true
%locations
%token <int> N
%type <int> E
%%
E: N { $$=$1; };
