from api import main_api

base_url = "https://api.reliefweb.int/v1/reports?appname=apidoc"


def get_reports_for_country(iso_code):
    reports = []

    for ocha_product in 20471, 12347, 12348, 12354:  # https://api.reliefweb.int/v1/references/ocha-products
        report = main_api.call_get(
            url=base_url + '&filter[operator]=AND'
                           '&filter[conditions][0][field]=primary_country.iso3'
                           '&filter[conditions][0][value]={0}'
                           '&filter[conditions][1][field]=ocha_product.id'
                           '&filter[conditions][1][value]={1}'
                           '&sort[]=score:desc'
                           '&sort[]=date:desc'
                           '&limit=1'
                .format(iso_code, ocha_product))['data']
        if len(report) > 0:
            response = main_api.call_get(report[0]['href'])['data'][0]['fields']
            reports.append(
                {'title': response['title'],
                 'thumbnail': response['file'][0]['preview']['url-large'],
                 'file': response['file'][0]['url']
                 })
    return reports
