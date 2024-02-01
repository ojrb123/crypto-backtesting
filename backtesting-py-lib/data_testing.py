import csv

with open('./data/LINK-USDT15-HULL-PSAR-SUPER.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    for row in reader:
        print(row)