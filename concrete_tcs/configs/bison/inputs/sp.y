%define lr.type ielr
%left 'a'
%define lr.keep-unreachable-state
%%
S:'a' A 'a'|'b' A 'b'|'c' c;
A:'a' 'a'|'a';
c:'a' 'b'|A;
