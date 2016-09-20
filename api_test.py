import requests
import pprint
from urllib import parse
import click

API = 'https://api.epistemonikos.org/v1'
CREDENTIALS = {
    'name': 'proyecto_software',
    'access_token': '1d3a64e690185658356fd1d025f88428'
}


def getinfo(document_id):
    url = '{baseurl}/documents/{id}'.format(baseurl=API, id=document_id)
    headers = {
        'Authorization': 'Token token={token}'.format(
            token=CREDENTIALS['access_token'])
    }

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return None
    data = res.json()
    return data


if __name__ == '__main__':
    tp = None

    while tp != 0 and tp != 1:
         tp = click.prompt("Epistemonikos ID(0) or DOI(1)?", type=int,
                           default=0)

    document_id = ''
    if tp == 0:
        document_id = click.prompt('Epistemonikos ID', type=str)
    else:
        tid = click.prompt('DOI', type=str)
        document_id = parse.quote(tid, safe='')

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(getinfo(document_id))
