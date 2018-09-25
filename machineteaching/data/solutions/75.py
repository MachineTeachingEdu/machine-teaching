def averaging(number_list):
    runningTotal = 0
    numberOfnumbers = len(number_list)
    # don't forget to initialise the running total before you start
    for count in range(numberOfnumbers):
        nextNumber = number_list[count]
        runningTotal = runningTotal + nextNumber
    average = runningTotal/numberOfnumbers
    return average
