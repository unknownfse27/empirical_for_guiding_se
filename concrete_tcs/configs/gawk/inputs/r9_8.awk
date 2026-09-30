BEGIN {
  foo[rand()] += 5
  for (x in foo);
  print x, foo[x]

  bar[rand()] = bar[rand()] + 5
  for (x in bar);
  print x, bar[x]
}
