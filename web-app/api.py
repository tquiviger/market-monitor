import requests
import json

base_url = "https://api.hpc.tools/v1/public"


def get_plan_list(country, year):
    response = call_api(url=base_url + '/plan/country/{0}'.format(country))
    print(response)
    return list(filter(lambda x: x['years'][0]['year'] == str(year), response))


def get_country_funding_by_orga(iso_code):
    response = call_api(
        url=base_url + '/fts/flow?countryiso3={0}&filterby=destinationyear:2018&groupby=organization'.format(iso_code))

    return {
        'country': iso_code,
        'total_funded': response['report1']['fundingTotals']['total'],
        'funding_source': response['report1']['fundingTotals']['objects'][0]['singleFundingObjects'],
        'funding_destination': response['report3']['fundingTotals']['objects'][0]['singleFundingObjects']
    }


def find_funding_for_cluster(funding_list, cluster):
    if cluster == 'Food Security':
        cluster_id = 6
    else:
        cluster_id = 9

    def myFilter(x):
        return x.get('id') == cluster_id

    return list(filter(myFilter, funding_list))[0]


def get_country_funding(plan_list):
    plan_list = list(map(lambda x: {'id': x.split('-')[0], 'name': x.split('-')[1]}, plan_list))
    plan_names = []
    funded_list = []
    required_list = []
    percentage_list = []
    for plan in plan_list:
        funded = 0
        required = 0
        percentage = 0
        plan_funding = call_api(url=base_url + '/fts/flow?planid={0}&groupby=globalcluster'.format(plan['id']))
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


def call_api(url):
    api_response = requests.get(url=url, headers={"Content-Type": "application/json"})
    if api_response.ok:

        # Loading the response data into a dict variable
        # json.loads takes in only binary or string variables so using content to fetch binary content
        return json.loads(api_response.content)['data']
    else:
        # If response code is not ok (200), print the resulting http error code with description
        api_response.raise_for_status()
