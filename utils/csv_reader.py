import pandas as pd

from conf import config


def get_simple_jme():
    return get_jme('jme_results.csv')


def get_detailed_jme():
    return get_jme('jme_detailed_results.csv')


def get_jme(file_name):
    return pd.read_csv(config.WORKING_FOLDER + file_name, sep=',',
                       dtype={'severe_wasting': float, 'wasting': float,
                              'stunting_children': int, 'severe_wasting_children': int,
                              'moderate_wasting_children': int,
                              'overweight': float, 'stunting': float, 'underweight': float,
                              'under5': int})


def get_relief_web():
    return pd.read_csv(config.WORKING_FOLDER + 'relief-web.csv', sep=',',
                       dtype={'crisis_index': int, 'crisis_name': str,
                              'crisis_iso3': str, 'figure_name': str,
                              'figure_date': str,
                              'figure_value': int, 'figure_source': str, 'figure_url': str})


def get_who_stunting():
    return get_who_dataset('who-stunting.csv')


def get_who_wasting():
    return get_who_dataset('who-wasting.csv')


def get_prevalence(row):

    try:
        return row['prevalence'].split(' ')[0]
    except IndexError:
        return 0


def get_lower(row):
    try:
        return row['prevalence'].split('[')[1].replace(']', '').split('-')[0]
    except IndexError:
        return 0


def get_upper(row):
    try:
        return row['prevalence'].split('[')[1].replace(']', '').split('-')[1]
    except IndexError:
        return 0


def get_who_dataset(filename):
    df = pd.read_csv(config.WORKING_FOLDER + filename, sep=',',
                     skiprows=1,
                     names=['UN_subregion', 'year', 'prevalence', 'number_children'],
                     dtype={'UN_subregion': str, 'year': int,
                            'prevalence': str, 'number_children': str})

    df['mean'] = df.apply(get_prevalence, axis=1).astype(float)
    df['lower'] = df.apply(get_lower, axis=1).astype(float)
    df['upper'] = df.apply(get_upper, axis=1).astype(float)
    return df


def get_un_rates():
    un_rates_df = pd.read_csv('conf/un_rates.csv', sep=';',
                              dtype={'currency': str, 'rate': float,
                                     'effective_date': str, 'month': int,
                                     'year': int})
    un_rates_df['usd_rate'] = 1 / un_rates_df['rate']
    return un_rates_df[['year', 'month', 'usd_rate']]


def get_wfp_tender_awards():
    return pd.read_csv(config.WORKING_FOLDER + 'wfp-tender-awards.csv', sep=',',
                       dtype={'date': str, 'year': int, 'month': int, 'tender_id': str, 'supplier': str,
                              'currency': str, 'destination': str, 'product': str, 'product_type': str,
                              'original_amount': float, 'amount_usd': float})
