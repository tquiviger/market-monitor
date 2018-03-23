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


def get_wfp_tender_awards():
    df = pd.read_csv(config.WORKING_FOLDER + 'wfp-tender-awards.csv', sep=',',
                     dtype={'date': str, 'supplier': str,
                            'product': str, 'value': str})
    df['value'] = df['value'].str.replace(" ", "").astype(float)
    return df
