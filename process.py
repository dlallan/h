import re
import nltk

#import nltk
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')

# https://www.nltk.org/api/nltk.tag.html

with open("input.txt") as f:
    text = f.read()
tokens = nltk.word_tokenize(text)
tagged = nltk.pos_tag(tokens)
#tagged = nltk.pos_tag(tokens, tagset="universal")

#for i in tagged:
#    print(i[0], i[1])

# list of tags: https://gist.github.com/nlothian/9240750#word-level
filtered_tags = {
    "JJ",   # adjectives
    "JJR",
    "JJS",
    "NNP",  # proper nouns
    "NNPS",
}

# list for consistant order
result_words = list()

# filters out through nlp
for i in tagged:
    if i[1] in filtered_tags:
        result_words.append(i)

# filters out non-alpha results
alpha = re.compile('[a-zA-Z]+')
alpha.match()


print(result_words)

