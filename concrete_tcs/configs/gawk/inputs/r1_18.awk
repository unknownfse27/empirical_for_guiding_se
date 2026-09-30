BEGIN {
  data = "foooobazbarrrrr"
  match(data, /(fo+).+(bar*)/, arr)

  for (i = 0; i in arr; i++) {
    printf("arr[%d] = \"%s\"\n", i, arr[i])
    printf("arr[%d, \"start\"] = %s, arr[%d, \"length\"] = %s\n",
           i, arr[i, "start"], i, arr[i, "length"])
  }

  char[1] = "."
  pat[1] = "[--\\/]"
  char[2] = "a"
  pat[2] = "[]-c]"
  char[3] = "c"
  pat[3] = "[[a-d]"
  char[4] = "\\"
  pat[4] = "\[-\]"
  char[5] = "[.c.]"
  pat[5] = "[a-[.e.]]"
  char[6] = "[.d.]"
  pat[6] = "[[.c.]-[.z.]]"

  for (i = 1; i in char; i++) {
    printf("\"%s\" ~ /%s/ --> %d\n",
           char[i], pat[i], char[i] ~ pat[i])
  }
}
