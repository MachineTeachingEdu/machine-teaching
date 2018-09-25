def common(list1, list2):
    common_list = []
    for i in list1:
        if i in list2 and i not in common_list:
            common_list.append(i)

    common_list.sort()
    return common_list
