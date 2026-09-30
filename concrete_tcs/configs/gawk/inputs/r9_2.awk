function print_count() {
  if (iteration)
    printf "Iteration%s # Total lines %s\n", iteration, linecnt
  iteration = linecnt = 0
}

NF == 0 { next }
/^[*]{10}/ { print_count(); next }

$2 == "Test#" {
  if (NR > 1)
    print ""
  print "TestCase #", $3
  next
}

$2 == "iteration" {
  print_count()
  iteration = $3
  next
}

iteration { linecnt++ }

END { print_count() }
