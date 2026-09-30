%code top { char*s="/*a*/";char c='}'; }
%code requires { /*}*/ }
%initial-action { char*p="\"}{"; }
%%
S: "a" { char*s="}\"/*";char c='\\'; /*}*/ } ;
