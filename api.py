import json

import requests

base_url = "https://api.hpc.tools/v1/public"


def get_plan_list(year):
    response = call_api(url=base_url + '/plan/year/{0}'.format(year))['data']
    return sorted(response, key=lambda x: x['name'])


def get_country_plan_list(country, year):
    response = call_api(url=base_url + '/plan/country/{0}'.format(country))['data']
    return list(filter(lambda x: x['years'][0]['year'] == str(year), response))


def get_wfp_funding():
    response_source = call_api(
        url=base_url + '/fts/flow?organizationAbbrev=wfp&year=2017,2018&filterby=destinationGlobalClusterId:6,'
                       '9&groupby=organization')['data']
    if len(response_source['report1']['fundingTotals']['objects']) == 0:
        funding_source = []
    else:
        funding_source = response_source['report1']['fundingTotals']['objects'][0]['singleFundingObjects']

    response_target = call_api(
        url=base_url + '/fts/flow?organizationAbbrev=wfp&year=2017,2018&filterby=destinationGlobalClusterId:6,'
                       '9&groupby=plan')['data']
    if len(response_target['report1']['fundingTotals']['objects']) == 0:
        funding_destination = []
    else:
        funding_destination = response_target['report3']['fundingTotals']['objects'][0]['singleFundingObjects']

    return {
        'total_funded': response_source['report1']['fundingTotals']['total'],
        'funding_source': funding_source,
        'funding_destination': funding_destination
    }


def get_all_nut_and_fs_funding(organization):
    response = call_api(
        url=base_url + '/fts/flow?year=2017,2018&globalClusterId=6,9&flowtype=standard&organizationAbbrev={0}'.format(
            organization))
    data = response['data']

    if len(data['flows']) == 0:
        flows = []
    else:
        flows = data['flows']
    while True:
        try:
            next_page_url = str.replace(response['meta']['nextLink'], 'v1/v1', 'v1')
        except Exception:
            next_page_url = ''
            pass
        if next_page_url == '':
            break
        else:
            response = call_api(url=next_page_url)
            flows = flows + response['data']['flows']
    return {
        'total_funded': data['incoming']['fundingTotal'],
        'flows': flows
    }


def get_country_funding_by_orga(iso_code):
    response = call_api(
        url=base_url + '/fts/flow?countryiso3={0}&filterby=destinationyear:2018&groupby=organization'.format(iso_code))[
        'data']
    if len(response['report1']['fundingTotals']['objects']) == 0:
        funding_source = []
        funding_destination = []
    else:
        funding_source = response['report1']['fundingTotals']['objects'][0]['singleFundingObjects']
        funding_destination = response['report3']['fundingTotals']['objects'][0][
            'singleFundingObjects']

    return {
        'country': iso_code,
        'total_funded': response['report1']['fundingTotals']['total'],
        'funding_source': funding_source,
        'funding_destination': funding_destination
    }


def find_funding_for_cluster(funding_list, cluster):
    if cluster == 'Food Security':
        cluster_id = 6
    else:
        cluster_id = 9

    def myFilter(x):
        return x.get('id') == cluster_id

    return list(filter(myFilter, funding_list))[0]


def get_country_funding_for_year(iso_code, year):
    plan_list = get_country_plan_list(iso_code, year)
    plan_names = []
    funded_list = []
    required_list = []
    percentage_list = []
    for plan in plan_list:
        funded = 0
        required = 0
        percentage = 0
        plan_funding = call_api(url=base_url + '/fts/flow?planid={0}&groupby=globalcluster'.format(plan['id']))['data']
        for cluster in ['Food Security', 'Nutrition']:
            try:
                required = find_funding_for_cluster(plan_funding['requirements']['objects'], cluster)[
                    'revisedRequirements']
            except Exception:
                pass
            try:
                funded = \
                    find_funding_for_cluster(
                        plan_funding['report3']['fundingTotals']['objects'][0]['singleFundingObjects'], cluster)[
                        'totalFunding']
            except Exception:
                pass
            try:
                percentage = str(round(funded / required * 100, 1)) + '%'
            except Exception:
                pass
            plan_names.append(plan['name'] + ' - ' + cluster)
            funded_list.append(funded)
            required_list.append(required)
            percentage_list.append(percentage)

    return {'total_funded': funded_list, 'required': required_list, 'percentages': percentage_list, 'plans': plan_names}


def get_country_funding_for_organization(iso_code, organization):
    response = call_api(
        url=base_url + '/fts/flow?countryiso3={0}&organizationAbbrev={1}&year=2017,2018&globalClusterId=6,9&groupby=organization'.format(
            iso_code, organization))[
        'data']
    if len(response['report1']['fundingTotals']['objects']) == 0:
        funding_source = []
    else:
        funding_source = response['report1']['fundingTotals']['objects'][0]['singleFundingObjects']

    return {
        'country': iso_code,
        'total_funded': response['report1']['fundingTotals']['total'],
        'funding_source': funding_source
    }


def find_food_security_funding(funding_list):
    def myFilter(x): return x.get('id') == 6

    return list(filter(myFilter, funding_list))[0]


def get_plan_funding(plan_list):
    plan_list = list(map(lambda x: {'id': x.split('-')[0], 'name': x.split('-')[1]}, plan_list))
    plan_names = []
    funded_list = []
    required_list = []
    percentage_list = []
    for plan in plan_list:
        funded = 0
        required = 0
        percentage = 0
        plan_funding = call_api(url=base_url + '/fts/flow?planid={0}&groupby=globalcluster'.format(plan['id']))['data']
        try:
            required = find_food_security_funding(plan_funding['requirements']['objects'])['revisedRequirements']
        except Exception:
            pass
        try:
            funded = \
                find_food_security_funding(
                    plan_funding['report3']['fundingTotals']['objects'][0]['singleFundingObjects'])[
                    'totalFunding']
        except Exception:
            pass
        try:
            percentage = str(round(funded / required * 100, 1)) + '%'
        except Exception:
            pass
        plan_names.append(plan['name'])
        funded_list.append(funded)
        required_list.append(required)
        percentage_list.append(percentage)

    return {'total_funded': funded_list, 'required': required_list, 'percentages': percentage_list, 'plans': plan_names}


def call_api(url):
    api_response = requests.get(url=url, headers={"Content-Type": "application/json"})
    if api_response.ok:

        # Loading the response data into a dict variable
        # json.loads takes in only binary or string variables so using content to fetch binary content
        return json.loads(api_response.content)
    else:
        # If response code is not ok (200), print the resulting http error code with description
        api_response.raise_for_status()
