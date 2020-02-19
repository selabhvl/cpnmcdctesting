- the original model was not syntactically valid due to labels introduced for readability.
  VS has eliminated the labels via a regex search-and-replace from "\(([ap]\d\d?)\)<" to "$1<".
  Another necessary single change was a label containing "." which does not comply to the required ML naming scheme for SSE.
