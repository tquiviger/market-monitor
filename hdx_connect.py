from hdx.hdx_configuration import Configuration
from hdx.data.dataset import Dataset
import xlrd
import unicodecsv
import pandas as pd
import os

WORKING_FOLDER = os.environ.get('WORKING_FOLDER', '/Users/thomas/work/nutriset/')


def get_dataset():
    Configuration.create(hdx_site='prod', user_agent='hdx', hdx_read_only=True)
    return Dataset.read_from_hdx('child-malnutrition-joint-country-dataset-unicef-who-world-bank-group-2017')


def download_dataset():
    dataset = get_dataset()
    resources = dataset.get_resources()
    url, path = resources[0].download(WORKING_FOLDER)

    return path


def xls2csv(xls_filename, csv_filename):
    wb = xlrd.open_workbook(xls_filename)
    sh = wb.sheet_by_index(0)

    fh = open(csv_filename, 'wb')
    csv_out = unicodecsv.writer(fh, encoding='utf-8')

    for row_number in range(sh.nrows):
        csv_out.writerow(sh.row_values(row_number))
    fh.close()


def get_total(row):
    return row['under5'] * 1000


def get_moderate_wasting(row):
    if row['wasting'] > 0 and row['severe_wasting'] > 0:
        return row['wasting'] - row['severe_wasting']
    else:
        return 0


def process_csv(source_file):
    market = pd.read_csv(source_file, sep=',', index_col=False)
    market = (market.iloc[14:])
    market.columns = ['iso_code', 'country_name', 'survey_year', 'year', 'UN_subregion', 'UN_region', 'SDG_region',
                      'UNICEF_region', 'WHO_region', 'WB_income_group', 'WB_region', 'WHO_todrop', 'survey_sample_size',
                      'severe_wasting', 'wasting', 'overweight', 'stunting', 'underweight', 'notes', 'report_author',
                      'source', 'under5']
    market.year = market.year.astype(float)
    market.under5 = market.under5.str.replace('-', '-1').astype(float)
    market.severe_wasting = market.severe_wasting.str.replace('-', '-1').astype(float)
    market.wasting = market.wasting.str.replace('-', '-1').astype(float)
    market.survey_sample_size = market.survey_sample_size.str.replace('-', '-1').astype(float)
    market.overweight = market.overweight.str.replace('-', '-1').astype(float)
    market.stunting = market.stunting.str.replace('-', '-1').astype(float)
    market.underweight = market.underweight.str.replace('-', '-1').astype(float)

    market = (market.fillna(-1).drop(columns=['WHO_todrop', 'survey_year']))
    market['under5'] = market.apply(get_total, axis=1).astype(int)
    market['year'] = market['year'].astype(int)
    market['moderate_wasting'] = market.apply(get_moderate_wasting, axis=1)

    market['stunting_children'] = (market['under5'] * market['stunting'] / 100)
    market['wasting_children'] = (market['under5'] * market['wasting'] / 100)
    market['severe_wasting_children'] = (market['under5'] * market['severe_wasting'] / 100)
    market['moderate_wasting_children'] = (market['under5'] * market['moderate_wasting'] / 100)
    market['overweight_children'] = (market['under5'] * market['overweight'] / 100)
    market['underweight_children'] = (market['under5'] * market['underweight'] / 100)

    market['stunting_children'] = market['stunting_children'].astype(int)
    market['severe_wasting_children'] = market['severe_wasting_children'].astype(int)
    market['moderate_wasting_children'] = market['moderate_wasting_children'].astype(int)
    market['wasting_children'] = market['wasting_children'].astype(int)
    market['overweight_children'] = market['overweight_children'].astype(int)
    market['underweight_children'] = market['underweight_children'].astype(int)

    market_to_save = market.set_index('iso_code')
    market_to_save.to_csv(WORKING_FOLDER + 'jme_detailed_results.csv', sep=',', encoding='utf-8')

    market['max_year'] = market.groupby(['iso_code'])['year'].transform(max)
    market_max = market[market.year == market.max_year]
    market_max = market_max.set_index('iso_code')
    market_max = (market_max.drop(columns=['max_year']))
    market_max.to_csv(WORKING_FOLDER + 'jme_results.csv', sep=',', encoding='utf-8')


def main():
    '''Download dataset from HDX'''

    output_file = WORKING_FOLDER + 'jme_source.csv'
    path = download_dataset()
    xls2csv(path, output_file)
    process_csv(output_file)


if __name__ == '__main__':
    main()
