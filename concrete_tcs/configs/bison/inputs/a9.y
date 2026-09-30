%token A B C
%%
list: %empty | list item;
item: A | B item | item C;
