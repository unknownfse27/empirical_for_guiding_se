%define lr.type ielr
%left "op"
%%
e: e "op" e | "x";
s: a "x" | b "y"; a: "z"; b: "z";