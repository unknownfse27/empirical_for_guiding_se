%define lr.type ielr
%%
S: a A c | b A d | a B d | b B c;
A: "e";
B: "e";
a: "a";
b: "b";
c: "c";
d: "d";
