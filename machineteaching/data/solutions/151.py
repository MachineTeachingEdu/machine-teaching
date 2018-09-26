def count(sentence):
    d={"uppercase":0, "lowercase":0}
    for char in sentence:
        if char.isupper():
            d["uppercase"]+=1
        elif char.islower():
            d["lowercase"]+=1
        else:
            pass
    return d
