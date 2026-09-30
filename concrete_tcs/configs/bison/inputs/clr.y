%define lr.type canonical-lr %locations %union{int v;}
%%
E:E '+' E|E '-' E|E '*' E|'(' E ')'|'a'|'b'|error;
