%define lr.type ielr
%define parse.lac full
%define lr.default-reduction consistent
%%
s:a a a a;
a:%empty|a "a"|"a" a;
