{
  gensub(/[aeiou]/, "", "g", $0)
  sub(/^/, "prefix-")
  sub(/$/, "-suffix")
  gsub(/o/, "0")
  gsub(/i/, "1")
  sub(/(.*)([0-9]{3})/, "\\1-\\2")
  sub(/(.*)([A-Z]{3})/, "\\1_\\2")
  sub(/(\b\w+\b)(\s+\1)+/, "\\1")
  sub(/(foo)(bar)/, function(m, a, b) { return a "baz" b })
  gsub(/./, function(m) { return tolower(m) })
  gsub(/[^\x00-\x7F]/, "")
  print $0
}
