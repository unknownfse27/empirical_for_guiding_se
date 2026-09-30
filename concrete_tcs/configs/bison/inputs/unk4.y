%printer{} foo baz
%destructor{} bar zap
%token foo "foo" bar "bar"
%left foo bar
%%
s:foo bar;