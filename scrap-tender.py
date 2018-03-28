import calendar
import urllib.request as urllib

import pandas as pd
from bs4 import BeautifulSoup

from utils import csv_reader


def process_supplier(row):
    supplier_name_lower = row['supplier'].lower()
    if 'nutriset' in supplier_name_lower:
        return 'NUTRISET'
    elif 'edesia' in supplier_name_lower:
        return 'EDESIA'
    elif 'compact' in supplier_name_lower:
        return 'COMPACT'
    elif 'nutrivita' in supplier_name_lower:
        return 'NUTRIVITA'
    elif 'hilina' in supplier_name_lower:
        return 'HILINA'
    elif 'jb' in supplier_name_lower:
        return 'JB'
    elif 'diva' in supplier_name_lower:
        return 'DIVA'
    elif 'insta' in supplier_name_lower:
        return 'INSTA'
    elif 'ismail' in supplier_name_lower:
        return 'ISMAIL'
    elif 'mana' in supplier_name_lower:
        return 'MANA'
    else:
        return supplier_name_lower


def get_product_type(row):
    product_name = row['product'].lower()
    if 'rutf' in product_name:
        return 'severe_wasting'
    elif 'lns-sq' in product_name:
        return 'stunting'
    elif 'nutributter' in product_name:
        return 'stunting'
    else:
        return 'wasting'


def get_currency(row):
    currency = row['amount'].split(' ')[0]
    if currency == 'EURO':
        return 'EUR'
    return currency


def process_amount(row):
    amount = pd.to_numeric(row['amount'].split(' ')[1].replace(',', '')).astype(float)
    return amount


def is_rsf(row):
    return 'RSF' in row['tender_id']


def process_month(row):
    return list(calendar.month_abbr).index(row.month_name[:3])


def process_final_amount(row):
    if row['currency'] == 'USD':
        return row['amount_clean']
    else:
        print(row['amount_clean'])
        print(row['usd_rate'])
        return row['amount_clean'] * row['usd_rate']


def main():
    data = []
    tenders = []
    current_year = 2018
    quote_page = 'http://www.wfp.org/procurement/food-tender-awards/' + str(current_year)
    page = urllib.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('table', attrs={'class': 'pure-table'})
    for tr in name_box.findAll("tr"):
        tds = tr.find_all('td')
        tds = [ele.text.strip() for ele in tds]
        data.append([ele for ele in tds if ele])

    current_month = ''
    for d in data:
        try:
            if len(d) == 1:
                current_month = d[0]
            elif d[0] == 'Supplier Name':
                pass
            else:
                tenders.append({
                    'year': current_year,
                    'month_name': current_month,
                    'supplier': d[0],
                    'product': d[1],
                    'tender_id': d[2],
                    'amount': d[3],
                    'destination': d[4]
                }
                )
        except Exception:
            pass

    df = pd.DataFrame(tenders)
    df['is_rsf'] = df.apply(is_rsf, axis=1)
    df['month'] = df.apply(process_month, axis=1)
    df = df[df['is_rsf']]
    df['supplier_clean'] = df.apply(process_supplier, axis=1)
    df['product_type'] = df.apply(get_product_type, axis=1)
    df['currency'] = df.apply(get_currency, axis=1)
    df['amount_clean'] = df.apply(process_amount, axis=1)

    df = pd.merge(df, csv_reader.get_un_rates(), how='left', on=['year', 'month'])
    df['final_amount'] = df.apply(process_final_amount, axis=1)
    print(df.head(10))

    # with open('index.csv', 'a') as csv_file:
    #     writer = csv.writer(csv_file)
    #     writer.writerow([datetime.now()])


if __name__ == '__main__':
    main()
