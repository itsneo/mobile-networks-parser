#!/usr/bin/env python

import argparse
import json

from pyquery import PyQuery as pq

wikipedia_url = 'https://en.wikipedia.org/wiki/%s'

lte_networks_pages = (
    'List_of_LTE_networks',
    'List_of_LTE_networks_in_Asia',
    'List_of_LTE_networks_in_Europe',
)

desired_cols = (
    'Country',
    'Operator',
    'B',
    'VoLTE',
)

def open_pages():
    for pagename in lte_networks_pages:
        yield pq(wikipedia_url % pagename)

def process_doc(doc):
    for col_index, table in find_tables(doc):
        yield process_table(col_index, table)

def find_tables(doc):
    tables_w_th = doc('table').find('th').parents('table')
    for table in tables_w_th:
        header_texts = [i.text().split()[0] for i in pq(table).find('th').parents('tr').eq(0).items('th')]
        if set(desired_cols).issubset(header_texts):
            col_index = list()
            for col in desired_cols:
                col_index.append(header_texts.index(col))
            yield col_index, table

def process_table(col_index, table):
    table = pq(table)
    country = str()
    col_index_wo_country = list()
    for tr in table.find('td').parents('tr'):
        pq_tr = pq(tr)
        if is_country_col(pq_tr.find('td').eq(col_index[0])):
            country = pq_tr.find('td').eq(col_index[0]).text()
            pq_tr.find('td').eq(col_index[0]).remove()
            col_index_wo_country = [x-1 for x in col_index[1:]]
        record = {'country': country}
        record.update(process_tr_w_tds(col_index_wo_country, pq_tr))
        yield record

def is_country_col(td):
    td = pq(td)
    return td('span').hasClass('flagicon')

def process_tr_w_tds(col_index_wo_country, pq_tr):
    return {
        'operator': pq_tr.find('td').eq(col_index_wo_country[0]).text(),
        'band': pq_tr.find('td').eq(col_index_wo_country[1]).text(),
        'volte': pq_tr.find('td').eq(col_index_wo_country[2]).text()
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process "List of LTE networks" from Wikipedia')
    parser.add_argument('--json', help='JSON output', action='store_true')
    args = parser.parse_args()
    docs = open_pages()
    result = [entry for doc in docs for doc_result in process_doc(doc) for entry in doc_result]
    if args.json:
        print(json.dumps(result))
    else:
        print(result)
