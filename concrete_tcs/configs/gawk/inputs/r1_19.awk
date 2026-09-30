BEGIN {
  printf "%*sworld\n", -20, "hello"
  printf("%'d\n", 123456789)
  printf("%'f\n", 123456789)

  file = "testit.txt"
  for (i = 1; i <= 3; i++) {
    print("line", i) > file
  }

  close(file)
  ARGV[1] = file
  ARGC = 2

  for (i = 1; i <= 3; i++) {
    getline
  }

  printf "NR should be 3, is %d\n", SYMTAB["NR"]
}
