def create_matrix(X, Y):
    rowNum = X
    colNum = Y
    multilist = [[0 for col in range(colNum)] for row in range(rowNum)]

    for row in range(rowNum):
        for col in range(colNum):
            multilist[row][col]= row*col

    return multilist
