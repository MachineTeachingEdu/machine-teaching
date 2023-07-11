def hex2dec(hexString):
    denary = 0
    lengthHex = len(hexString)
    for element in range(lengthHex):
        hexSeg = hexString[element]
        if hexSeg == 'A':
            hexSeg = 10
        elif hexSeg == 'B':
            hexSeg = 11
        elif hexSeg == 'C':
            hexSeg = 12
        elif hexSeg == 'D':
            hexSeg = 13
        elif hexSeg == 'E':
            hexSeg = 14
        elif hexSeg == 'F':
            hexSeg = 15
        else:
            hexSeg = int(hexSeg)

        #work out the place value power of 16
        placePower = 16**(lengthHex-(element+1))
        hexSeg = hexSeg * placePower
        denary = denary + hexSeg

    return denary
     
