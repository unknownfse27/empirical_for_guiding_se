%{
int tp_var;
%}
%define api.token.prefix {TK_} %define api.symbol.prefix {SY_} %define api.token.raw
%%
S: 'a';
%%
int tp_main(){return 0;}
