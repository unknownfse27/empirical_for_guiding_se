BEGIN {
  FS = "("
  count = 0
}

/([a-zA-Z_][a-zA-Z_0-9]*[(][^)]*[)][[:space:]]*{)/ {
  p = 1
}

p && /([a-zA-Z_][a-zA-Z_0-9]*[[:space:]]+[a-zA-Z_][a-zA-Z_0-9]*[[:space:]]*;)/ {
  count++
}

p && /}/ {
  p = 0
}

END {
  print "Total local variables:", count
}
