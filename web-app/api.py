import requests
import json

base_url = "https://api.hpc.tools/v1/public"


def get_plan_list(year):
    response = call_api(url=base_url + '/plan/year/{0}'.format(year))
    return sorted(response, key=lambda x: x['name'])


def get_country_funding_by_orga(iso_code):
    response = call_api(
        url=base_url + '/fts/flow?countryiso3={0}&filterby=destinationyear:2018&groupby=organization'.format(iso_code))

    return {'total_funded': response['report1']['fundingTotals']['total']}


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
        plan_funding = call_api(url=base_url + '/fts/flow?planid={0}&groupby=globalcluster'.format(plan['id']))
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
        return json.loads(api_response.content)['data']
    else:
        # If response code is not ok (200), print the resulting http error code with description
        api_response.raise_for_status()
