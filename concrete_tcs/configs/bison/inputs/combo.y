%define lr.type ielr%define api.push-pull both%define parse.lac full%printer{puts("p");}<*>%destructor{puts("d");}<>%token A B
%%
S:A|B;
