BEGIN {
  format = PROCINFO["strftime"]
  exitval = 0

  if (ARGC > 2)
    exitval = 1
  else if (ARGC == 2) {
    format = ARGV[1]
    if (format ~ /\+/)
      format = substr(format, 2)
  }

  print strftime(format)
  exit exitval
}
