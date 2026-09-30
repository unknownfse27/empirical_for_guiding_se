%union{int i;float f;}%token<i> I "\x1A"%token<f> F "\u00A0"%initial-action{@$.first_line=1;}
%%
S:I F|F I;
