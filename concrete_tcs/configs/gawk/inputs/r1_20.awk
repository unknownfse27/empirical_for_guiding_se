BEGIN {
  print "Goes to a file out1" > "_out1"
  print "Normal print statement"
  print "This printed on stdout" > "/dev/stdout"
  print "You blew it!" > "/dev/stderr"
  PREC = 113
  printf("%0.25f\n", 0.1)
}
