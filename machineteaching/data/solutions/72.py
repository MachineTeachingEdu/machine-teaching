def vote_and_retire(age):
    sentence = ""
    if age >= 16:
        sentence = "You are old enough to vote."
    else:
        ageToVote = 16 - age
        sentence = "You can vote in {0} years.".format(ageToVote)
         
    if age < 65:
        ageToRetire = 65 - age
        sentence += " You can retire in {0} years.".format(ageToRetire)

    return sentence
