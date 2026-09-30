%language "Java"
%define api.package {org.gnu.bison}
%define api.parser.class {TestParser}
%define parse.error custom
%define parse.trace
%lex-param {Lexer lexer}
%%
s: 'j';
