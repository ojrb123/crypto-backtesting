import csv

with open('./data/LINK-USDT60.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    for row in reader:
        print(row)