%token A B X Y
%expect 99
%expect-rr 99
%%
e:A B %expect 5|A B %expect 5|A|A B X|A B X|A B Y|A B Y;
f:Y %expect 1|Y %expect 2;