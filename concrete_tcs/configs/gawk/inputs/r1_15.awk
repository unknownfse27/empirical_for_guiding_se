BEGIN {
  srand()

  for (i = 1; i <= num1; i++) {
    for (j = 1; j <= num2; j++) {
      arr[i, j] = rand()
    }
  }

  PROCINFO["sorted_in"] = "@val_num_desc"

  for (i in arr) {
    print i, arr[i]
  }
}
