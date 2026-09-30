%define lr.type ielr
%define lr.default-reduction accepting
%nonassoc "a"
%%
start: cons "a" | "b" cons "c" ;
cons: "a" dr | "a" dr "a" | "a" sh ;
dr: %empty ;
sh: "b" ;
