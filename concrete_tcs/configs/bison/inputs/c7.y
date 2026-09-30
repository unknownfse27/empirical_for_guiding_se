%left + -%right * /%nonassoc = %%token N%nterm E
%%
E:N|E + E|E - E|E * E|E / E|E % E|E = E|%empty;
