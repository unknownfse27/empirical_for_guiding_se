%union{int v; char* s;}
%token <v> NUM
%token <s> STR
%type <v> E
%%
P: E{printf("%d",$1);}|STR{printf("%s",$1);};
E: NUM{$$=$1;}|E"+"E{$$=$1+$3;}|E"*"E{$$=$[E1]*$[E2];}|"("E")"{$$=$[E];};
