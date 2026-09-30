%define lr.type ielr
%nonassoc "a"
%destructor {;} "a"
%%
start: er ce "a" ;
er: "a" "a" cr ce "a" | "a" error;
cr: %empty ;
ce: "a" | %empty %prec "a" ;
start: "b" ce "b" ;
