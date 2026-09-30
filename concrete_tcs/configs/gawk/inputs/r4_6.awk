{
  for (i = 1; i <= NF; i++)
    lengths[length($i)]++
}

END {
  for (len in lengths)
    printf("%2d %s\n", len, "█" * lengths[len])
}
