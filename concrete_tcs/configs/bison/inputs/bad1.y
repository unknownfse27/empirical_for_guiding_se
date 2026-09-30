%{int x; /* unclosed
%define api.invalid {[
%token A <bad>
%%
S:A{$$=$;@$=@;};
