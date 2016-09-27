# coding = utf-8
import requests
import tldextract
import csv
import traceback
import sys
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
        self.domain_dois = {}

    def __repr__(self):
        return '''
        Urls: {dict}
        Sample Dois: {samples}
        Valid URLs: {urlt}
        Invalid URLS: {urlf}
        Valid DOIs: {doit}
        Invalid DOIs: {doif}
        '''.format(dict=self.url_dict,
                   urlt=self.url_true,
                   urlf=self.url_false,
                   doit=self.doi_true,
                   doif=self.doi_false,
                   samples=self.domain_dois)

    def __str__(self):
        return self.__repr__()

    def join(self, struct):
        self.url_true += struct.url_true
        self.url_false += struct.url_false
        self.doi_true += struct.doi_true
        self.doi_false += struct.doi_false

        for k, v in struct.url_dict.items():
            self.url_dict[k] = self.url_dict.get(k, 0) + struct.url_dict[k]

        for k, v in struct.domain_dois.items():
            if k not in self.url_dict.keys():
                self.url_dict[k] = v


def extract_domain(url):
    e = tldextract.extract(url)
    return "{domain}.{suffix}".format(domain=e.domain, suffix=e.suffix)


def verify_doi(doi, info):
    doi_url = 'http://dx.doi.org/' + doi
    if doi and (not (doi == '')) and (doi[0] != '/'):
        info.doi_true += 1
        try:
            r = requests.get(doi_url, allow_redirects=True)
            # url = r.headers.get('Location', None)
            url = r.url  # <- Returns last url in chain of redirects.
            if url:
                info.url_true += 1
                final_url = extract_domain(url)
                info.url_dict[final_url] = info.url_dict.get(final_url, 0) + 1
                if final_url not in info.domain_dois.keys():
                    info.domain_dois[final_url] = doi_url
            else:
                info.url_false += 1
        except Exception:
            info.doi_false += 1

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
    try:
        for i, doi in enumerate(doi_list):
            verify_doi(doi, info_struct)

            if i % 50 == 0:
                print('Thread ' + str(thread_id))
                print('i: ' + str(i))
                print(info_struct)
                print()

                logger.info('\nTotal: {tot}\nStruct: {struct}\n'.format(tot=i,
                                                                        struct=info_struct))

        print('Thread ' + str(thread_id))
        print('Done!')
        logger.info('\n * --- * Done * --- *')
    except Exception:
        logger.error(traceback.format_exc())


def read_doi_tsv(tsv_file):
    dois = []
    with open(tsv_file, encoding='utf-8') as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        for line in tsvreader:
            dois.append(line[1].strip())

    n_threads = 7
    split_len = len(dois) / n_threads
    threads = []
    info_structs = []

    for i in range(0, n_threads):
        init = int(split_len * i)
        end = int(init + split_len)
        split = dois[init:end]
        info = InfoStruct()
        t = threading.Thread(target=analyze_doi_list,
                             args=(split, info, i + 1))
        info_structs.append(info)
        threads.append(t)

        t.start()

    for t in threads:
        t.join()

    final_info = InfoStruct()
    for info in info_structs:
        final_info.join(info)

    with open('results', 'w', encoding='utf-8') as result_file, \
            open('samples', 'w', encoding='utf-8') as sample_file:
        writer = csv.writer(result_file, dialect='excel-tab')
        writer2 = csv.writer(sample_file, dialect='excel-tab')
        for domain, count in final_info.url_dict.items():
            writer.writerow([domain, count])
        for domain, doi in final_info.domain_dois.items():
            writer2.writerow([domain, doi])


if __name__ == '__main__':
    read_doi_tsv(sys.argv[1])
