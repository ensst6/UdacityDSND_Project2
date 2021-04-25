import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.colors
from collections import OrderedDict
import requests


# default list of all countries of interest
# here we are using income categories instead of individual countries
country_default = OrderedDict([('High Income', 'HIC'), ('Upper Middle Income', 'UMC'),
  ('Lower Middle Income', 'LMC'), ('Low Income', 'LIC'), ('World', 'WLD')])

def return_figures(countries=country_default, start_year=1990, end_year=2014):
  """Creates four plotly visualizations using the World Bank API

  # Example of the World Bank API endpoint:
  # arable land for the United States and Brazil from 1990 to 2015
  # http://api.worldbank.org/v2/countries/usa;bra/indicators/AG.LND.ARBL.HA?date=1990:2015&per_page=1000&format=json

    Args:
        country_default (dict): list of countries for filtering the data

    Returns:
        list (dict): list containing the four plotly visualizations

  """

  # prepare filter data for World Bank API
  # the API uses ISO-3 country codes separated by ;
  country_filter = list(countries.values())
  country_filter = [x.lower() for x in country_filter]
  country_filter = ';'.join(country_filter)

  # date range = start_year:end_year
  # default 1990-2014 is b/c electricity consumption ends at 2014 and
  # most sets start at 1990
  dt_range = str(start_year)+':'+str(end_year)


  # World Bank indicators of interest for pulling data
  indicators = ['EG.ELC.RNEW.ZS', 'EG.ELC.FOSL.ZS', 'EG.USE.ELEC.KH.PC', 'EN.ATM.CO2E.PC']

  data_frames = [] # stores the data frames with the indicator data of interest
  urls = [] # url endpoints for the World Bank API

  # pull data from World Bank API and clean the resulting json
  # results stored in data_frames variable
  payload = {'format': 'json', 'per_page': '2000', 'date':dt_range}
  for indicator in indicators:
    url = 'http://api.worldbank.org/v2/country/' + country_filter +\
    '/indicators/' + indicator
    urls.append(url)

    try:
      r = requests.get(url, params=payload)
      data = r.json()[1]
    except:
      print('could not load data ', indicator)

    for i, value in enumerate(data):
      value['indicator'] = value['indicator']['value']
      value['country'] = value['country']['value'].title()

    data_frames.append(data)

  # track # graphs for final append step
  # first chart plots % of electricity output from renewables 1990-2014 by
  # income category as a line chart, and includes world data as a comparator
  df_one = pd.DataFrame(data_frames[0])

  # this  country list is re-used by all the charts to ensure legends have the same
  # order and color
  country_list = list(countries.keys())

  graph_title = '% of Electricity from Renewable Sources by Income Category'
  y_title = '% Renewables'
  graph_one, layout_one = plot_line_all(df_one, graph_title, y_title, country_list)

  # second chart plots % of electricity output from fossil fuels 1990-2014 by
  # income category as a line chart, and includes world data as a comparator
  df_two = pd.DataFrame(data_frames[1])

  graph_title = '% of Electricity from Fossil Fuels by Income Category'
  y_title = '% Fossil Fuels'
  graph_two, layout_two = plot_line_all(df_two, graph_title, y_title, country_list)

  # third chart is bar plot of worldwide % renewable & % fossil fuels by year
  graph_three = []

  graph_three.append(
      go.Bar(
          x = df_one[df_one['country']=='World']['date'].tolist(),
          y = df_one[df_one['country']=='World']['value'].tolist(),
          name = 'Renewables'
          )
  )
  graph_three.append(
      go.Bar(
          x = df_two[df_two['country']=='World']['date'].tolist(),
          y = df_two[df_two['country']=='World']['value'].tolist(),
          name = 'Fossil Fuels'
          )
  )

  layout_three = dict(title = 'Worldwide Electricity Production by % Renewable & % Fossil Fuel\
<br> 1990 to 2014',
                xaxis = dict(title = 'Year',
                             autotick=False, tick0=start_year, dtick=4),
                yaxis = dict(title = '% of Electricity Production',
                             autotick=False, tick0=0, dtick=10),
                barmode = 'group')

  # fourth chart plots per-capita electricity consumption 1990-2014 by
  # income category as a line chart, and includes world data as a comparator
  # note that for this dataset, the "low income" group has no data
  df_four = pd.DataFrame(data_frames[2])
  # get rid of the empty "low income" group
  df_four = df_four[df_four['country'] != 'Low income']
  country_nolo = country_list[:3] + country_list[4:]

  # the <sub> tag was only way I could figure out to subtitle
  # there's a long post about using "annotations" in layout, but it didn't work
  # and was much more complicated
  graph_title = 'Per-Capita Electricity Use by Income Category<br><sub>\
(No data for low-income countries)</sub>'
  y_title = 'KWh Electricity per Person'
  graph_four, layout_four = plot_line_all(df_four, graph_title, y_title, country_nolo)

  # fifth chart plots per-capita CO2 emissions 1990-2014 by
  # income category as a line chart, and includes world data as a comparator
  df_five = pd.DataFrame(data_frames[3])

  graph_title = 'Per-Capita CO2 Emissions by Income Category'
  y_title = 'Metric Tons CO2 per Person'
  graph_five, layout_five = plot_line_all(df_five, graph_title, y_title, country_list)

  # sixth chart plots CO2 per capita/electricity consumption per capita
  df_six = df_four[['country','date','value']]
  df_six.rename(columns={'value':'pc_elec'}, inplace=True)
  df_six = df_six.merge(df_five[['country','date','value']],on=['country','date'])
  df_six.rename(columns={'value':'pc_co2'}, inplace=True)
  df_six['value'] = 1000.0*df_six['pc_co2']/df_six['pc_elec']

  graph_title = 'CO2 Emissions per Unit Electricity Consumption<br><sub>\
(No electricity data for low-income countries)</sub>'
  y_title = 'Kg CO2/KWh Electricity'
  graph_six, layout_six = plot_line_all(df_six, graph_title, y_title, country_nolo)

  # seventh chart is % renewable vs per-capita electricity for all years
  graph_seven = []
  df_seven = df_one[['country','date','value']]
  df_seven.rename(columns={'value':'pct_renew'}, inplace=True)
  df_seven = df_seven.merge(df_four[['country','date','value']],on=['country','date'])
  df_seven.rename(columns={'value':'pc_elec'}, inplace=True)

  for country in country_nolo:
      x_val = df_seven[df_seven['country'] == country]['pc_elec'].tolist()
      y_val =  df_seven[df_seven['country'] == country]['pct_renew'].tolist()
      graph_seven.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = country
          )
      )

  layout_seven = dict(title = '% Renewable Electricity Production by Per-Capita \
Electricity Use<br><sub>(No electricity data for low-income countries)</sub>\
<br> Data for 1990 to 2014',
                xaxis = dict(title = 'KWh Electricity Use per Person'),
                yaxis = dict(title = '% Renewable')
                )

   # append all charts
  figures = []
  figures.append(dict(data=graph_one, layout=layout_one))
  figures.append(dict(data=graph_two, layout=layout_two))
  figures.append(dict(data=graph_three, layout=layout_three))
  figures.append(dict(data=graph_four, layout=layout_four))
  figures.append(dict(data=graph_five, layout=layout_five))
  figures.append(dict(data=graph_six, layout=layout_six))
  figures.append(dict(data=graph_seven, layout=layout_seven))

  return figures

def plot_line_all(df, graph_title, y_title, countries, start_year=1990,\
                  end_year=2014, d_tick=4):
  """Creates a line plot for all years and categories

    Args:
        df (dataframe): contains country or other demographic category in "country",
                        data value of interest in "value", dates in "date"

        graph_title (string): Main title of graph; 2nd line by default is year range

        y_title (string): Title/label for y-axis

        countries (list): list of country or other category in plotting order

        start_year (int): starting year for plot

        end_year (int): ending year for plot

    Returns:
        graph (list): list of graph attributes for plotly visualization

        layout (list): list of chart formatting attributes for plotly visualization

  """

  df_plt = df[(df['date'].astype(int) >= start_year) & (df['date'].astype(int) <= end_year)]
  graph = []

  for country in countries:
      x_val = df_plt[df_plt['country'] == country]['date'].tolist()
      y_val =  df_plt[df_plt['country'] == country]['value'].tolist()
      graph.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = country
          )
      )

  layout = dict(title = graph_title + '<br>'\
+str(start_year)+' to '+str(end_year),
                xaxis = dict(title = 'Year',
                  autotick=False, tick0=start_year, dtick=d_tick),
                yaxis = dict(title = y_title),
                )

  return graph, layouts
