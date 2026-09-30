%define lr.type canonical-lr %nonassoc '=' %left '+' %% e: e '=' e | e '+' e | 'a';
