%define parse.error detailed %% stmt: 'i' e 't' stmt | 'i' e 't' stmt 'e' stmt | 'x'; e: E1; E1: E2; E2: E3; E3: 'e';
