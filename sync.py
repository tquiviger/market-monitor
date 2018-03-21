from hdx.hdx_configuration import Configuration
from hdx.data.dataset import Dataset
import xlrd
import unicodecsv
import pandas as pd
import os

WORKING_FOLDER = os.environ.get('WORKING_FOLDER', '/Users/thomas/work/nutriset/')


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
    market['under5'] = market.apply(get_total, axis=1)

    market_to_save = market.set_index('iso_code')
    market_to_save.to_csv(WORKING_FOLDER + 'jme_detailed_results.csv', sep=',', encoding='utf-8')

    market['max_year'] = market.groupby(['iso_code'])['year'].transform(max)
    market_max = market[market.year == market.max_year]
    market_max = market_max.set_index('iso_code')
    market_max = (market_max.drop(columns=['max_year']))
    market_max.to_csv(WORKING_FOLDER + 'jme_results.csv', sep=',', encoding='utf-8')


def main():
    '''Download dataset from HDX'''

    Configuration.create(hdx_site='prod', user_agent='A_Quick_Example', hdx_read_only=True)
    dataset = Dataset.read_from_hdx('child-malnutrition-joint-country-dataset-unicef-who-world-bank-group-2017')
    resources = dataset.get_resources()

    url, path = resources[0].download(WORKING_FOLDER)
    print('Resource URL %s downloaded to %s' % (url, path))
    output_file = WORKING_FOLDER + 'jme_source.csv'
    xls2csv(path, output_file)
    process_csv(output_file)


if __name__ == '__main__':
    main()
