def sort(shopping_list):
    #bubble sort list
    noMoreSwaps = False
    while not noMoreSwaps:
        noMoreSwaps = True
        for element in range(len(shopping_list)-1):
            if shopping_list[element] > shopping_list[element+1]:
                noMoreSwaps = False
                temp = shopping_list[element]
                shopping_list[element] = shopping_list[element+1]
                shopping_list[element+1] = temp
    return shopping_list
