import urllib.request as urllib

import pandas as pd
from bs4 import BeautifulSoup


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


def is_rsf(row):
    return 'RSF' in row['tender_id']


def process_amount(row):
    return row


def get_un_rates():


def main():
    data = []
    tenders = []
    quote_page = 'http://www.wfp.org/procurement/food-tender-awards/2017'
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
                print('Month {}'.format(current_month))
            elif d[0] == 'Supplier Name':
                pass
            else:
                tenders.append({
                    'year': 2018,
                    'month': current_month,
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
    df = df[df['is_rsf']]
    df['supplier_clean'] = df.apply(process_supplier, axis=1)
    df['product_type'] = df.apply(get_product_type, axis=1)
    df['currency'] = df.apply(get_currency, axis=1)

    print(df.head(10))
    # with open('index.csv', 'a') as csv_file:
    #     writer = csv.writer(csv_file)
    #     writer.writerow([datetime.now()])


if __name__ == '__main__':
    main()
