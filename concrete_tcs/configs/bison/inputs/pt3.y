%left A
%right B
%nonassoc C
%precedence D
%%
s:s A s|s B s|s C s|s D s|A;
