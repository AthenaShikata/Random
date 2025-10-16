import csv

input_file = "Sensors.csv"
output_file = "output.csv"

collumn1 = 2
collumn2 = 3

with open(input_file, newline='', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        # Make sure the row has enough columns
        if len(row) > max(collumn1,collumn2):
            row[collumn1], row[collumn2] = row[collumn2], row[collumn1]
        writer.writerow(row)