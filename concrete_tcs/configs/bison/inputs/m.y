%debug
%printer{fprintf(yyo,"%d",@$);}<>
%destructor{fprintf(stderr,"D%d\n",@$);}<>
%printer{;}<*>
%destructor{;}<*>
%%
s:{@$=1;}{$$=0;@$=2;}{$$=0;@$=3;}{@$=4;}"c"{$$=0;};
