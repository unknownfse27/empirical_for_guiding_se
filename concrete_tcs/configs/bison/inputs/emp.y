%define lr.type ielr %token A B
%%
S:A|B|C|%empty|S A|S B|S C|error;C:%empty;
