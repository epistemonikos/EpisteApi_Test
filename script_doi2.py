import requests
import re
import csv

import threading
import logging
from logging.handlers import RotatingFileHandler


class InfoStruct:
    def __init__(self):
        self.url_dict = {}
        self.url_true = 0
        self.url_false = 0
        self.doi_true = 0
        self.doi_false = 0

    def __repr__(self):
        return '''
        Urls: {dict}
        Valid URLs: {urlt}
        Invalid URLS: {urlf}
        Valid DOIs: {doit}
        Invalid DOIs: {doif}
        '''.format(dict=self.url_dict,
                   urlt=self.url_true,
                   urlf=self.url_false,
                   doit=self.doi_true,
                   doif=self.doi_false)

    def __str__(self):
        return self.__repr__()

    def join(self, struct):
        self.url_true += struct.url_true
        self.url_false += struct.url_false
        self.doi_true += struct.doi_true
        self.doi_false += struct.doi_false

        for k, v in struct.url_dict.items():
            self.url_dict[k] = self.url_dict.get(k, 0) + struct.url_dict[k]


def extract_domain(url):
    cut1 = re.search(r'//\S*?/', url).group(0)
    cut1 = cut1[2:len(cut1) - 1]
    cut1 = cut1.split('.')
    l = len(cut1)
    direction = cut1[l - 2] + '.' + cut1[l - 1]
    return direction


def verify_doi(doi, info):
    doi_url = 'http://dx.doi.org/' + doi
    if doi and (not (doi == '')) and (doi[0] != '/'):
        info.doi_true += 1
        r = requests.get(doi_url, allow_redirects=False)
        url = r.headers.get('Location', None)
        if url:
            info.url_true += 1
            final_url = extract_domain(url)
            info.url_dict[final_url] = info.url_dict.get(final_url, 0) + 1
        else:
            info.url_false += 1
    else:
        info.doi_false += 1


def analyze_doi_list(doi_list, info_struct, thread_id):
    logger = logging.getLogger('Thread ' + str(thread_id))
    logger.setLevel(logging.DEBUG)

    handler = RotatingFileHandler('thread{}.log'.format(thread_id),
                                  maxBytes=2048)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s]: %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    for i, doi in enumerate(doi_list):
        verify_doi(doi, info_struct)

        if i % 50 == 0:
            print('Thread ' + str(thread_id))
            print('i: ' + str(i))
            print(info_struct)
            print()

            logger.info('\nTotal: {tot}\nStruct: {struct}\n'.format(tot=i,
                                                                    struct=info_struct))


def read_doi_tsv():
    dois = []
    with open("episte_dois.tsv") as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        for line in tsvreader:
            dois.append(line[1].strip())

    half_1 = dois[:(int(len(dois) / 2))]
    half_2 = dois[(int(len(dois) / 2)):]

    info_struct1 = InfoStruct()
    info_struct2 = InfoStruct()

    t1 = threading.Thread(target=analyze_doi_list, args=(half_1,
                                                         info_struct1, 1))
    t2 = threading.Thread(target=analyze_doi_list, args=(half_2,
                                                         info_struct2, 2))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    info_struct1.join(info_struct2)

    with open('results', 'w') as file:
        writer = csv.writer(file, dialect='excel-tab')
        for key, value in info_struct1.url_dict.items():
            writer.writerow([key, value])


if __name__ == '__main__':
    read_doi_tsv()
