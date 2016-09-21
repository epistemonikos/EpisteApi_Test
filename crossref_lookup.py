import requests
import pprint
import sys

CROSSREFAPI = 'http://api.crossref.org/works'
            # 'http://search.crossref.org/dois'
DOIAPI = 'http://dx.doi.org/{doi}'


def citation_lookup(citation):
    params = {'query': citation.strip()}
    rv = requests.get(CROSSREFAPI, params=params).json()

    return rv['message']['items'][0]

    best_result = rv[0]
    return best_result

    # doi = best_result.get("doi", None)
    # if not doi:
    #    return None
    # print(doi)

    # headers = {'Accept': 'application/json'}
    # rv = requests.get(DOIAPI.format(doi=doi), headers=headers)
    # return rv


if __name__ == '__main__':
    citation = sys.stdin.read()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(citation_lookup(citation))
