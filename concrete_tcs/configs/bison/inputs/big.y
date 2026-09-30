%token A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
%expect 9
%expect-rr 3
%%
s:e|a|b|c;
e:A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|e A e|e B e|e C e;
a:A B;
b:A B;
c:A B;
