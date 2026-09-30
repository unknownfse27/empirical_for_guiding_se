%nonassoc '"a"' '"b"' '"c"'
%%
s: '"a"'|ea '"a"'|'"b"'|eb '"b"'|'"c"'|ec '"c"';
ea:%prec '"a"';
eb:%prec '"b"';
ec:%prec '"c"';
