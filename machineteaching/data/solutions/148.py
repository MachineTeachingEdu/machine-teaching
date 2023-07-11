def binby5(number_csv):
    value = []
    items=[x for x in number_csv.split(',')]
    for p in items:
        intp = int(p, 2)
        intp = int(p[0])*8 + int(p[1])*4 + int(p[2])*2 + int(p[3])
        if not intp%5:
            value.append(p)
    return ", ".join(value)
