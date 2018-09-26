def count(sentence):
    d={"digits":0, "letters":0}
    for char in sentence:
        if char.isdigit():
            d["digits"]+=1
        elif char.isalpha():
            d["letters"]+=1
        else:
            pass
    return d
