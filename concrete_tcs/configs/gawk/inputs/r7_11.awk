/^[[:space:]]*(int|void|char|float|double)[[:space:]]+[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*\([^)]*\)[[:space:]]*{/ {
  ++functions
}

END {
  print "Total functions:", functions, "\nTotal lines of code:", NR
}
