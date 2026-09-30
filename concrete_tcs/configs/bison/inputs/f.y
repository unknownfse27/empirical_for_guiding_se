%language "d" %define lr.type ielr %define parse.lac full %% E: E "+" E | E "*" E | "a";
