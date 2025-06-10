!python -m spacy download en_core_web_md

!pip install spacy_layout

import spacy
from spacy_layout import spaCyLayout

nlp = spacy.load("en_core_web_md")
layout = spaCyLayout(nlp)

doc = layout("/content/EbenezerMLEResume (1).pdf")

[i for i in doc.spans["layout"] if i.label_ == "section_header"]

def extract(string, doc):
  headings = [i for i in doc.spans["layout"] if i.label_ == "section_header"]
  res, match_ = [], headings[0]
  token = nlp(string)
  print(match_.similarity(token))
  for heading in headings[1:]:
    print(heading.similarity(token))
    if heading.similarity(token) > match_.similarity(token):
      match_ = heading
  ind = headings.index(match_)
  start, stop = match_.id, headings[ind+1].id
  for j in range(start+1, stop):
    res.append(doc.spans["layout"][j])
  return res
