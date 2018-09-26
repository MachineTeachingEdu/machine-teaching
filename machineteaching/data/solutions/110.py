def dec2bin(decimalNumber):
    binaryString = ""
    if decimalNumber == 0:
        binaryString = "00000000"
    else:
        while decimalNumber > 0:
            #work out whether a 0 or 1 goes in the next position
            positionValue = str(decimalNumber % 2)
            #append to string
            binaryString = positionValue + binaryString
            #
            decimalNumber = decimalNumber // 2
     
    #make sure number has eight bits
    addZeros = 0
    if len(binaryString) < 8:
        addZeros = 8 - len(binaryString)
    for eachZero in range(addZeros):
        binaryString = "0" + binaryString
    return binaryString
