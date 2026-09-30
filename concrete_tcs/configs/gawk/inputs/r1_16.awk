{
  gsub(/[\r\n]/, "", $NF)
}

END {
  asorti(fields)

  for (i = 1; i <= NF; i++)
    printf "%s%s", fields[i], (i == NF ? RS : "|")

  for (k in a) {
    for (i = 1; i <= NF; i++)
      printf "%s%s", a[k][i], (i == NF ? RS : "|")
  }
}
