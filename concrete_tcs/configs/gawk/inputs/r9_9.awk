BEGIN {
  num = $1
  for (divisor = 2; divisor * divisor <= num; divisor++) {
    if (num % divisor == 0)
      break
  }

  if (num % divisor == 0)
    printf "Smallest divisor of %d is %d\n", num, divisor
  else
    printf "%d is prime\n", num
}
