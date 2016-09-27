import csv

with open('episte_dois.tsv', 'r') as infile, open(
        'episte_dois.filtered.tsv', 'w') as outfile:

    reader = csv.reader(infile, delimiter='\t')
    writer = csv.writer(outfile, dialect='excel-tab')

    for line in reader:
        if line[0] == 'systematic-review':
            writer.writerow(line)
