%glr-parser
%token A B
%%
r: A %expect 1 %expect 0 | A B %expect-rr 1 %expect-rr 0;
q: A | A;
z: r %dprec 1 | q %dprec 1 ;
