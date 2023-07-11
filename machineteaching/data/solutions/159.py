def word_freq(sentence):
    freq = {}   # frequency of words in text
    for word in sentence.split():
        freq[word] = freq.get(word,0)+1

    return freq
