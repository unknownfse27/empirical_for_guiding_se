%yacc
%left <int> A B
%right <float> C 258 D
%type X <int> Y <float> Z
%token <int> M N
%token P 257
%define api.value.union.name "MyU"
%%
s:A B|C D|M N|P|X Y Z;
X:M;Y:N;Z:M N;
