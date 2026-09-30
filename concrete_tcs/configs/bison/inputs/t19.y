%token A
%destructor { free($$); } <*>
%printer { fprintf(yyo, "tok"); } <>
%%
s:A;
%%
