{
  for (i = 1; i <= NF; i++)
    count[tolower($i)]++
}

END {
  for (word in count)
    printf "%s: %d\n", word, count[word]
}
