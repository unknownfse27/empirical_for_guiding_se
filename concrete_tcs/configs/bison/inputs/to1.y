%token A "??!" B "??/" C "\a" D "\b" E "\f" F "\n" G "\r" H "\t" I "\v" J "\123" K "\x4a" L "\?" M "\7"
%type <int> s
%printer {;} <int>
%%
s:A|B|C|D|E|F|G|H|I|J|K|L|M;
