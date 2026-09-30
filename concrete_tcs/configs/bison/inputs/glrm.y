%glr-parser
%expect 1
%expect-rr 2
%token A B
%%
p:s;
s:a %dprec 1|b %dprec 2|c %merge<mrg>;
a:A B;
b:A B;
c:A %?{1} B|A %?{2} B;
