from pathlib import Path
from geopy.geocoders import Nominatim
import requests
import pandas as pd

class CityNotFoundError(Exception):
  def __init__(self,msg):
     super().__init__(msg)

class ForecastUnavailable(Exception):
  def __init__(self,msg):
     super().__init__(msg)


def get_forecast( city='Pittsburgh' ):
    '''
    Returns the nightly's forecast for a given city.

    Inputs:
    city (string): A valid string

    Output:
    period (dictionary/JSON): a dictionary containing at least, the forecast keys startTime, endTime and detailedForecast.

    Throws:
    CityNotFoundError if geopy returns empty list or if the latitude longitude fields are empty.

    ForecastUnavailable if the period is empty or the API throws any status code that is not 200

    Hint:
    * Return the period that is labeled as "Tonight"
    ''' 
    geolocator = Nominatim(user_agent="ModernProgramming")
    location = geolocator.geocode(city)
    latitude = location.latitude
    longitude = location.longitude

    if(latitude is None or longitude is None):
      raise CityNotFoundError("Latitude and Longitude fields are empty.")

    URL = f'https://api.weather.gov/points/{latitude},{longitude}'
    response = requests.get(URL)
    if(response.status_code != 200):
      raise ForecastUnavailable("Period is empty or the API throws any status code that is not 200.")

    details = response.json()
    forecast_link = details['properties']['forecast']
    response = requests.get(forecast_link)
    details = response.json()
    info = details['properties']['periods']

    for i in range(len(info)):
      if(info[i]["name"] == "Tonight"):
        startTime = info[i]['startTime']
        endTime = info[i]['endTime']
        detailedForecast = info[i]['detailedForecast']

    period = {"startTime" : startTime, "endTime" : endTime, "detailedForecast" : detailedForecast}

    if(len(period) == 0):
      raise ForecastUnavailable("Period is empty or the API throws any status code that is not 200.")
    else:
      return period

def main():
    period = get_forecast()

    file = 'weather.pkl'

    if Path(file).exists():
        df = pd.read_pickle( file )
    else:
        df = pd.DataFrame(columns=['Start Date', 'End Date', 'Forecast'])

    df = df.append({'Start Date': period['startTime'], 'End Date': period['endTime'], 'Forecast': period['detailedForecast']}, ignore_index=True)
    df = df.drop_duplicates()
    df.to_pickle(file)

    #sort repositories
    file = open("README.md", "w")
    file.write('![Status](https://github.com/janvi-mirchandani/python-get-forecast/actions/workflows/build.yml/badge.svg)\n')
    file.write('![Status](https://github.com/janvi-mirchandani/python-get-forecast/actions/workflows/pretty.yml/badge.svg)\n')
    file.write('# Pittsburgh Nightly Forecast\n\n')
    
    file.write(df.to_markdown(tablefmt='github'))
    file.write('\n\n---\nCopyright © 2022 Pittsburgh Supercomputing Center. All Rights Reserved.')
    file.close()

if __name__ == "__main__":
    main()
