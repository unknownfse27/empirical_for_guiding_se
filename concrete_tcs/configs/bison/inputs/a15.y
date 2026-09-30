%require "3.7"
%error-verbose
%name-prefix "foo"
%parse-param { char const *fn }
%initial-action { }
%token <int> NUM
%type <int> exp
%destructor { } <int>
%printer { } <int>
%%
exp: NUM { $$ = $1; };
