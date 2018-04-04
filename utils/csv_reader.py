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


def get_sdg_indicators():
    return pd.read_csv('conf/sdg-indicators.csv', sep=',',
                       dtype={
                           'location_id': int,
                           'location_name': str,
                           'year_id': int,
                           'estimate_type': str,
                           'indicator_id': int,
                           'indicator_short': str,
                           'ihme_indicator_description': str,
                           'indicator_is_mdg': str,
                           'indicator_outline': str,
                           'indicator_unit': str,
                           'target_description': str,
                           'goal_description': str,
                           'unscaled_value': float,
                           'unscaled_lower': float,
                           'unscaled_upper': float
                       })
