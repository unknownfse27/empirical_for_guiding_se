%glr-parser
%expect-rr 2
%locations
%token<int>A B
%nterm<int>s a b c
%destructor{}<int>
%%
s:a|b|c|A B;a:A B %dprec 1{$$=@1.first_line;};b:A B %dprec 2{$$=@2.last_column;};c:A %merge<m>;
