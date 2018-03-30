from api import main_api

base_url = "https://api.reliefweb.int/v1/reports?appname=apidoc"


def get_reports_for_country(iso_code):
    reports = []
    response = main_api.call_get(
        url=base_url + '&query[fields][]=country.iso3&query[value]={0}&filter[field]=ocha_product.id&filter[value]=20471&sort[]=date:desc'
            .format(iso_code))
    if len(response['data']) > 0:
        for report in response['data'][0:3]:
            response = main_api.call_get(report['href'])['data'][0]['fields']
            reports.append(
                {'title': response['title'],
                 'thumbnail': response['file'][0]['preview']['url-thumb'],
                 'file': response['file'][0]['url']
                 })
    return reports


if __name__ == '__main__':
    get_reports_for_country('SOM')
