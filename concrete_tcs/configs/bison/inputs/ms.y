%token END 0 "e" A ":=" I "i" N "n"
%start u a e
%%
u:a e;
a:%empty|a i;
i:A ":=" e;
e:"i" e e|"n";
