%token E 0 "e" A ":=" I "i"
%token <int> D "id" N "n"
%type <int> d e
%%
%start u;u:a e;a:%empty|a s;s:d ":=" e;d:"id";e:"i" e <int>{$$=1;} <int>{$$=2;} e|"(" e ")"|"id"|"n";