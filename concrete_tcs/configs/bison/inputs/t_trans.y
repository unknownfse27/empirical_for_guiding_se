%glr-parser
%token EOF_TOK 0 "end of file"
%token UNDEF_TOK 256 "invalid token"
%token A _("Translated A")
%%
S: A %?{ 1 } | A %?{ 0 } | EOF_TOK | UNDEF_TOK ;
