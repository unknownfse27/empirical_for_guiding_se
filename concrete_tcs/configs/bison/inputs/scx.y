%define api.value.automove true %locations %union{int i;} %token <i> a-b N %type <i> e %% e:a-b[x] {$$=$x+$0+$-1; @$=@x;}|e[v] "+" {$<i>$=$v;} e[v] {$$=$v+$1;};
