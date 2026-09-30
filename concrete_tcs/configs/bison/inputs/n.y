%nonassoc A B C
%left D
%token A B C D
%%
s:A|a A|B|b B|C|c C|d C|e C;
a:%empty %prec A;
b:%empty %prec B;
c:%empty %prec C;
d:%empty %prec C;
e:%empty %prec D;
