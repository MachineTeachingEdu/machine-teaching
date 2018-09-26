def bin2hex(binaryString):
    hexA = binaryString[:4]
    hexB = binaryString[4:]
    finalhex = ""
    for eachSegment in (hexA, hexB):
        denary = int(eachSegment[0])*8 + int(eachSegment[1])*4 + int(eachSegment[2])*2 + int(eachSegment[3])*1
        if denary == 10:
            denary = 'A'
        elif denary == 11:
            denary = 'B'
        elif denary == 12:
            denary = 'C'
        elif denary == 13:
            denary = 'D'
        elif denary == 14:
            denary = 'E'
        elif denary == 15:
            denary = 'F'

        finalhex = finalhex + str(denary)
    return finalhex
