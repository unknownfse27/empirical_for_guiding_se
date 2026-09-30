%token A
%%
e[outer]: A {$outer; $<int>outer; @outer;} A[inner] {$outer; $inner; $<int>inner; @inner;};
