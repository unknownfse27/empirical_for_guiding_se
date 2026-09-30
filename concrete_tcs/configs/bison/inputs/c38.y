%define api.pure%define parse.error verbose%default-prec%define api.prefix {old}%token A B
%%
S:A B;
