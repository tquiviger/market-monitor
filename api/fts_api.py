from api import main_api

base_url = "https://api.hpc.tools/v1/public"


def get_plan_list(year):
    response = main_api.call_get(url=base_url + '/plan/year/{0}'.format(year))['data']
    if not response:
        return []
    return sorted(response, key=lambda x: x['name'])


def get_country_plan_list(country, year):
    response = main_api.call_get(url=base_url + '/plan/country/{0}'.format(country))['data']
    if not response:
        return []
    return list(filter(lambda x: x['years'][0]['year'] == str(year), response))


def get_wfp_funding():
    response_source = main_api.call_get(
        url=base_url + '/fts/flow?organizationAbbrev=wfp&year=2017,2018&filterby=destinationGlobalClusterId:'
                       '9&groupby=organization')['data']
    if not response_source:
        return {
            'total_funded': 0,
            'funding_source': [],
            'funding_destination': []
        }
    if len(response_source['report1']['fundingTotals']['objects']) == 0:
        funding_source = []
    else:
        funding_source = response_source['report1']['fundingTotals']['objects'][0]['singleFundingObjects']

    response_target = main_api.call_get(
        url=base_url + '/fts/flow?organizationAbbrev=wfp&year=2017,2018&filterby=destinationGlobalClusterId:'
                       '9&groupby=plan')['data']
    if not response_target:
        return {
            'total_funded': 0,
            'funding_source': [],
            'funding_destination': []
        }
    if len(response_target['report1']['fundingTotals']['objects']) == 0:
        funding_destination = []
    else:
        funding_destination = response_target['report3']['fundingTotals']['objects'][0]['singleFundingObjects']

    return {
        'total_funded': response_source['report1']['fundingTotals']['total'],
        'funding_source': funding_source,
        'funding_destination': funding_destination
    }


def get_nutrition_funding_for_orga(organization):
    response = main_api.call_get(
        url=base_url + '/fts/flow?year=2015,2016,2017,2018&globalClusterId=9&flowtype=standard&organizationAbbrev={0}'
            .format(organization))

    data = response['data']
    if not data:
        return {
            'total_funded': 0,
            'flows': []
        }
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
            response = main_api.call_get(url=next_page_url)
            flows = flows + response['data']['flows']
    return {
        'total_funded': data['incoming']['fundingTotal'],
        'flows': flows
    }


def get_country_funding_by_orga(iso_code, year):
    response = main_api.call_get(
        url=base_url + '/fts/flow?countryiso3={0}&globalClusterId=9&filterby=destinationyear:{1}&groupby=organization'.format(
            iso_code, year))[
        'data']
    if not response:
        return {
            'country': iso_code,
            'total_funded': 0,
            'funding_source': [],
            'funding_destination': []
        }
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


def find_funding_for_nutrition(funding_list):
    def myFilter(x):
        return x.get('id') == 9

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
        plan_funding = \
            main_api.call_get(url=base_url + '/fts/flow?planid={0}&groupby=globalcluster'.format(plan['id']))['data']
        if not plan_funding:
            pass
        try:
            required = find_funding_for_nutrition(plan_funding['requirements']['objects'])[
                'revisedRequirements']
        except Exception:
            pass
        try:
            funded = \
                find_funding_for_nutrition(
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


def get_country_funding_for_organization(iso_code, organization):
    response = main_api.call_get(
        url=base_url + '/fts/flow?countryiso3={0}&organizationAbbrev={1}&year=2017,2018&globalClusterId=9&groupby=organization'.format(
            iso_code, organization))[
        'data']
    if not response:
        return {
            'country': iso_code,
            'total_funded': 0,
            'funding_source': []
        }
    if len(response['report1']['fundingTotals']['objects']) == 0:
        funding_source = []
    else:
        funding_source = response['report1']['fundingTotals']['objects'][0]['singleFundingObjects']

    return {
        'country': iso_code,
        'total_funded': response['report1']['fundingTotals']['total'],
        'funding_source': funding_source
    }


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
        plan_funding = \
            main_api.call_get(url=base_url + '/fts/flow?planid={0}&groupby=globalcluster'.format(plan['id']))['data']
        if not plan_funding:
            pass
        try:
            required = find_funding_for_nutrition(plan_funding['requirements']['objects'])['revisedRequirements']
        except Exception:
            pass
        try:
            funded = \
                find_funding_for_nutrition(
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
