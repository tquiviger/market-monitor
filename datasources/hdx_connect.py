import os

import pandas as pd
import unicodecsv
import xlrd
from hdx.data.dataset import Dataset
from hdx.hdx_configuration import Configuration

from conf import config, nutriset_config


def get_jme_dataset():
    print("Downloading latest version of Joint Malnutrition Dataset from HDX")
    return Dataset.read_from_hdx('child-malnutrition-joint-country-dataset-unicef-who-world-bank-group-2017')


def get_reliefweb_dataset():
    print("Downloading latest version of Relief Web Crisis App Dataset from HDX")
    return Dataset.read_from_hdx('reliefweb-crisis-app-data')


def download_dataset(dataset, filename):
    resources = dataset.get_resources()
    url, path = resources[0].download(config.WORKING_FOLDER)
    os.rename(path, config.WORKING_FOLDER + filename)


def xls2csv(xls_filename, csv_filename):
    wb = xlrd.open_workbook(config.WORKING_FOLDER + xls_filename)
    sh = wb.sheet_by_index(0)

    fh = open(csv_filename, 'wb')
    csv_out = unicodecsv.writer(fh, encoding='utf-8')

    for row_number in range(sh.nrows):
        csv_out.writerow(sh.row_values(row_number))
    fh.close()


def x1000(row):
    return row['under5'] * 1000


def get_rutf_needs_kg(row):
    return row['severe_wasting_children'] * nutriset_config.SEVERE_WASTING_KG_PER_CHILDREN


def get_rusf_lns_mq_needs_kg(row):
    return row['moderate_wasting_children'] * nutriset_config.MODERATE_WASTING_KG_PER_CHILDREN


def get_lns_sq_needs_kg(row):
    return row['stunting_children'] * nutriset_config.STUNTING_KG_PER_CHILDREN


def get_moderate_wasting(row):
    if row['wasting'] > 0 and row['severe_wasting'] > 0:
        return row['wasting'] - row['severe_wasting']
    else:
        return 0


def process_jme_csv(source_file):
    market = pd.read_csv(source_file, sep=',', index_col=False)
    market = (market.iloc[14:])
    market.columns = ['iso_code', 'country_name', 'survey_year', 'year', 'UN_subregion', 'UN_region', 'SDG_region',
                      'UNICEF_region', 'WHO_region', 'WB_income_group', 'WB_region', 'WHO_todrop', 'survey_sample_size',
                      'severe_wasting', 'wasting', 'overweight', 'stunting', 'underweight', 'notes', 'report_author',
                      'source', 'under5']
    market.year = market.year.astype(float)
    market.under5 = market.under5.str.replace('-', '-1').astype(float)
    for col_name in ['stunting', 'wasting', 'severe_wasting', 'overweight', 'underweight']:
        market[col_name] = market[col_name].str.replace('-', '-1').astype(float)

    market = (market.fillna(0).drop(columns=['WHO_todrop', 'survey_year']))
    market['under5'] = market.apply(x1000, axis=1).astype(int)
    market['year'] = market['year'].astype(int)
    market['moderate_wasting'] = market.apply(get_moderate_wasting, axis=1).astype(float)

    for col_name in ['stunting', 'wasting', 'severe_wasting', 'moderate_wasting', 'overweight', 'underweight']:
        market[col_name + '_children'] = (market['under5'] * market[col_name] / 100)
        market[col_name + '_children'] = market[col_name + '_children'].astype(int)

    market['severe_wasting_needs_kg'] = market.apply(get_rutf_needs_kg, axis=1).astype(int)
    market['moderate_wasting_needs_kg'] = market.apply(get_rusf_lns_mq_needs_kg, axis=1).astype(int)
    market['wasting_needs_kg'] = market['severe_wasting_needs_kg'] + market['moderate_wasting_needs_kg']
    market['stunting_needs_kg'] = market.apply(get_lns_sq_needs_kg, axis=1).astype(int)

    market_to_save = market.set_index('iso_code')
    market_to_save.to_csv(config.WORKING_FOLDER + 'jme_detailed_results.csv', sep=',', encoding='utf-8')
    print("File successfully exported to {0}".format(config.WORKING_FOLDER + 'jme_detailed_results.csv'))

    market['max_year'] = market.groupby(['iso_code'])['year'].transform(max)
    market_max = market[market.year == market.max_year]
    market_max = market_max.set_index('iso_code')
    market_max = (market_max.drop(columns=['max_year']))
    market_max.to_csv(config.WORKING_FOLDER + 'jme_results.csv', sep=',', encoding='utf-8')
    print("File successfully exported to {0}".format(config.WORKING_FOLDER + 'jme_results.csv'))


def main():
    Configuration.create(hdx_site='prod', user_agent='read-hdx', hdx_read_only=True)

    output_file = config.WORKING_FOLDER + 'jme_source.csv'
    download_dataset(dataset=get_jme_dataset(), filename='jme.xls')
    xls2csv('jme.xls', output_file)
    process_jme_csv(output_file)

    download_dataset(dataset=get_reliefweb_dataset(), filename='relief-web.csv')


if __name__ == '__main__':
    main()
