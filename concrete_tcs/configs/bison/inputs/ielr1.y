%define lr.type ielr%define lr.default-reduction consistent%define parse.lac full%define api.push-pull push%token A B C
%%
S:A B S|B C S|C A S|%empty{};
