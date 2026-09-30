%left A B
%%
S: A { } %prec B A | %empty %prec A;
