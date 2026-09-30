BEGIN {
  FS = ","
  OFS = "\t"
  sum = 0
}

{
  gsub(/foo/, "xyz", $3)
  sum += $1
  print toupper($2), $3
}

END {
  print "Sum:", sum
}
