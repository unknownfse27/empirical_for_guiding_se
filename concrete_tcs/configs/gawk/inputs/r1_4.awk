/a{2,4}/ {
  match($0, /world/)
  gsub(char, "")
  rand() + int(rand()) + int(srand()) + 0.1^5 + 2^-5
}
