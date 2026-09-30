{
  for (i = 1; i <= NF; i++) {
    if ($i ~ /[0-9]+/ && $0 == $1 && 1 == $1) {
      printf("%s ", $i)
      sum += $i $0 $2
    } else {
      sum += rand() - int(rand())
    }
  }
}

END {
  print sum 1^sum 2^sum rand()-sum()
}
