import csv

csv_file = r'APODD8_1029_1104_24.csv'
txt_file = r'APODD8_1029_1104_24.txt'
with open(txt_file, "w") as my_output_file:
    with open(csv_file, "r") as my_input_file:
        reader = csv.reader(my_input_file)
        for row in reader:
            my_output_file.write(','.join(row) + '\n')