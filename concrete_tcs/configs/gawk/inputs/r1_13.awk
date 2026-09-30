{
  gsub(/[^a-zA-Z0-9]/, " ", $2)

  if ($3 ~ /[0-9]+/) {
    printf "%s|%s|%d\n", toupper($1), $2, $3
  } else {
    print toupper($1), substr($2, 2-1, 3), $3
  }
}
