import requests, re
import csv

dictionary = {}
url_true = 0
url_false = 0
doi_true = 0
doi_false = 0

def extract_domain(url):
    cut1 = re.search(r'//\S*?/', url).group(0)
    cut1 = cut1[2:len(cut1)-1]
    cut1 = cut1.split('.')
    l = len(cut1)
    direction = cut1[l-2] + '.' + cut1[l-1]
    return direction

def printf(doi):
    url = 'http://dx.doi.org/'+ doi
    match_doi = re.match('^10.\d{4,9}/[-._;()/:A-Z0-9]+$', doi)
    if doi and (not (doi == '')) and (doi[0] != '/'):
        global doi_true
        doi_true += 1
        r = requests.get(url, allow_redirects=False)
        url = r.headers.get('Location', None)
        if url:
            global url_true
            url_true += 1
            global dictionary
            final_url = extract_domain(url)
            dictionary[final_url] = dictionary.get(final_url, 0)
            dictionary[final_url] = dictionary[final_url] + 1
        else:
            global url_false
            url_false += 1
    else:
        global doi_false
        doi_false += 1



def reader_dois(func):
    with open("episte_dois.tsv") as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        count = -1
        for line in tsvreader:
          count += 1
          if count % 10 == 0:
              global dictionary
              global url_true
              global url_false
              global doi_true
              global doi_false
              print '----------- ' + str(count)
              print url_true
              print url_false
              print doi_true
              print doi_false
              print dictionary
          if line[1:]:
            func(line[1:][0])


f = lambda x: printf(x)
reader_dois(f)
with open('results', 'w') as file:
    writer = csv.writer(file, dialect='excel-tab')
    for key, value in dictionary.iteritems():
        writer.writerow([key, value])
