# Market Monitor

Mashup application that gathers data from multiple Humanitarian Open Data Sources and creates vizualizations for Market Analysis purpose.

## Data Sources

* [HDX Platform](https://data.humdata.org/) - HDX Platform to download JME file and Relief Web Crisis App data
* [FTS](https://fts.unocha.org/) - FTS Api to gather funding for countries, organizations, plans
* [Relief Web](https://reliefweb.int/) - Relief Web API to collect reports for each country
* [WFP Tender Awards](https://www.wfp.org/procurement/food-tender-awards) - WFP Tender Awards webpage scrapped to gather tender data


## Usage

##### Install

```sh
pip install -r requirements.txt
```


##### Launching

 ```sh
python index.py [-d]
 ```

 The -d option activates the debug mode
