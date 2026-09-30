/^[[:space:]]*[^{}#][[:alpha:]_][[:alnum:]_[:space:]]*\(/ {
  match($0, /^[[:space:]]*([^[:space:]]+\s+)*(\S+)\s*\(/, a)
  printf "function_call: %s (line %s)\n", a[2], FNR
}
