%token N I F T E W D %left '+' '*' %right '=' %nonassoc X E %% s:%empty|s a; a:e';'|F e T a %prec X|F e T a E a|W e D a|error';'; e:N|I|I'='e|e'+'e|e'*'e|e e|'('e')';
