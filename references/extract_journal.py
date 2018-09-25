import csv



def extract_journals(filename):

    education = {}
    cs = {}
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for item in reader.readline():
            print(item)


if __name__ == '__main__':

