import requests

from conf import config


def main():
    files = \
        [{
             'url': 'http://apps.who.int/gho/athena/data/xmart.csv?target=GHO/NUTSEVWASTINGPREV,NUTSEVWASTINGNUM&profile=crosstable&filter=COUNTRY:-;UNREGION:*&x-sideaxis=UNREGION;YEAR&x-topaxis=GHO',
             'filename': 'who-wasting.csv'},
         {
             'url': 'http://apps.who.int/gho/athena/data/GHO/NUTSTUNTINGPREV,NUTSTUNTINGNUM?filter=COUNTRY:-;REGION:-;UNREGION:*&x-sideaxis=UNREGION;YEAR&x-topaxis=GHO&profile=crosstable&format=csv',
             'filename': 'who-stunting.csv'}]

    for file in files:
        r = requests.get(file['url'])
        with open(config.WORKING_FOLDER + file['filename'], 'wb') as f:
            f.write(r.content)


if __name__ == '__main__':
    main()
