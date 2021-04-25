# World Bank API Energy Use Data Dashboard

This is a Flask app that visualizes data from the [World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation). Data are
pulled directly from the API and then visualized using [Plotly](https://plotly.com/).

The data selected for this dashboard relate to energy production and consumption. The files the app pulls from are:
- [Renewable energy output (% of total electricity output)](https://data.worldbank.org/indicator/EG.ELC.RNEW.ZS)
- [Electricity production from oil, gas, and coal (% of total)](https://data.worldbank.org/indicator/EG.ELC.FOSL.ZS)
- [Electric power consumption (KWh per capita)](https://data.worldbank.org/indicator/EG.USE.ELEC.KH.PC)
- [CO2 emissions (metric tons per capita)](https://data.worldbank.org/indicator/EN.ATM.CO2E.PC)  

The data are stratified by income categories:
- Low Income: Gross national income ([GNI](https://en.wikipedia.org/wiki/Gross_national_income)) per capita < $1036
- Lower Middle Income: GNI per capita $1,036 - $4,045
- Upper Middle Income: GNI per capita $4,046 - $12,535
- High Income: GNI per capita > $12,535
- World: Worldwide average for comparison  

The data span various years. Because the renewable data begin at 1990, and the electricity consumption data (as of April 2021) end at 2014, the graphs default to 1990-2014. Also, there are no data for electricity consumption for the low-income category, so that graph and the two derived from it will not display the low-income stratum.  

This is a project developed for the Udacity Data Scientist Nanodegree.

## Getting Started

To use the web app, follow the link below:  
[https://world-bank-energy-dashboard.herokuapp.com](https://world-bank-energy-dashboard.herokuapp.com)


Plotly tools allowing customization of each visualization will display above it.  
The `Filter by Income Category` menu allows customization of which income categories are displayed. Note that the third plot only contains world-level data and so will not display if `World` is de-selected.

## Prerequisites

To install the Flask app, you need:
- python3
- python packages in the `requirements.txt` file

 Install the packages with
```
 pip install -r requirements.txt
```

## Customizing

To customize the app, modify `scripts/data.py` to change the data sources and number and type of plots.  
You will only need to edit `worldbankapp/routes.py` If you change the categories (e.g., to plot by country or region instead of income). Update the `country_codes` list, which controls the filter.  
If you want to change the layout, menus, etc., edit the `templates\index.html` file.  Obviously if you're deploying this for your own project, change LinkedIn and Github URLs to your own pages.

To run and debug the app locally, un-comment the last line in `worldbankapp.py`:   
```
# app.run(host='0.0.0.0', port=3001, debug=True)
```  
then run:  
```
python3 worlbankapp.py
```  
and open `http://0.0.0.0:3001/` in your browser.  

## History
Created April 25, 2021

## License  
[Licensed](license.md) under the [MIT License](https://spdx.org/licenses/MIT.html).
