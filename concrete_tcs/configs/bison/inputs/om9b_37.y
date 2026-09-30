%locations
%token A "??!"
%printer{;} <*>
%destructor{;} <*>
%%
s:A { @$=@1; };
