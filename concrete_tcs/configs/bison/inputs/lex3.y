%type <a.b> c
%printer { $<foo>$ } <bar>
%destructor { $$ } <baz>
%left "foo"
%right "bar"
%nonassoc "baz"
%% s:;
