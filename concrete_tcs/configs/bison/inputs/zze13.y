%destructor { destroy($$); } <> <>
%printer { print($$); } <> <>
%%
s: %empty ;
%destructor { destroy($$); } <>
%printer { print($$); } <>
