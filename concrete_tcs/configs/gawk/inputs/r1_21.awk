BEGIN {
  e = "1(e)"
  ex = "3e2(ex)"
  x = "6e5(x)"

  print e+0, x+0
  print 0x
  print 0e+x
  print 0ex
  print 010e2
  print 0e9.3

  dfapat[1] = data[1] = "b\323"
  dfapat[2] = data[2] = "b\362"
  dfapat[3] = data[3] = "b\363"

  regexpat[1] = "[a-c]\323"
  regexpat[2] = "[a-c]\362"
  regexpat[3] = "[a-c]\363"

  IGNORECASE = 1

  for (i = 1; i <= 3; i++) {
    for (j = 1; j <= 3; j++) {
      printf("data[%d] ~ dfa[%d] = %s\n",
             i, j, data[i] ~ dfapat[j] ? "ok" : "bad")
      printf("data[%d] ~ regex[%d] = %s\n",
             i, j, data[i] ~ regexpat[j] ? "ok" : "bad")
    }
  }
}
