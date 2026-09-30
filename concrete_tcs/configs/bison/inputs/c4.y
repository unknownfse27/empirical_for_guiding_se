%language "java"%locations%code imports{import java.io.*;}%code lexer{/*L*/}%define parse.error verbose%token<Integer> NUM
%type<Integer> expr
%%
expr:NUM;
