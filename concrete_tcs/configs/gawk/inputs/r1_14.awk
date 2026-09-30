{
  if (FNR == 1)
    print "Header1", "Header2", "Header3"

  if ($3 > 1000) {
    $1 = toupper($1)
    gsub(/[aeiou]/, "", $2)
    sub(/(.*)([0-9]{3})/, "\1_\2")
    sub(/(.*)([A-Z]{3})/, "\1-\2")
    gsub(/o/, "0", $4)
    sub(/foo/, "bar", $5)
    print $1, $2, $4, $5
  }
}
