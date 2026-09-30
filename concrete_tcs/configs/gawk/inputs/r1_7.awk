{
  if ($3 < 1000) {
    print gsub(/&nbsp;/, " ")
    gsub(/<\/?[a-zA-Z]+[^>]*>/, "")
    gsub(/\s+/, " ")
    gsub(/<(b|i|u)>|<\/(b|i|u)>/, "")
    "abc\n " $1 " abc"
  } else {
    print "abc" $1 " abc"
  }
}
