%union{int v;}
%token<v>N
%type<v>e s
%%
i:"if" e[exp.v] "then" s[id]{$[i]=$exp.v+$id;};
e:N[a]{$$=$a;};s:N;
