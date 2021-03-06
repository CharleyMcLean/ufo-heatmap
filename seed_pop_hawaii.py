import csv

import geocoder

from model import CityPop, connect_to_db, db
from server import app


def get_lat_lng(city, state):
    """Geocode the given city (in this case a county) and state."""
    # Printing for debugging purposes.
    print city, state
    geocode_result = geocoder.arcgis(city + ", " + state)

    #status will be "OK" if a usable result comes back; if so, return it
    status = geocode_result.json["status"]
    if status == "OK":
        lat = geocode_result.json["lat"]
        lng = geocode_result.json["lng"]
        return lat, lng
    #otherwise, return None
    else:
        return None


def load_city_populations():
    """Load population data from census csv file into database"""

    # Open the csv file and create a reader object; convert to list for iteration.
    populationFile = open("/home/vagrant/src/project/seed_data/population-hawaii.csv")
    populationReader = csv.reader(populationFile)
    populationData = list(populationReader)

    total_added = 0

    for row in populationData:
        # Only gathering information for the geographic summary areas
        # coresponding to the code '050' (counties).
        if row[0] == '050':
            # Row indices obtained from census documentation.
            # Population data is based on the 2010 census.
            city = row[8]
            state = row[9]

            # A few random rows have a letter at this position.
            if type(row[10]) is int:
                population = row[10]
            else:
                population = row[11]

            lat_lng = get_lat_lng(city, state)
                # If lat_lng exists, capture the values of latitude and longitude.
                
            if lat_lng:
                # Unpack the list.
                latitude, longitude = lat_lng

            # If lat_lng is None, then geocoding did not return a result.
            else:
                print "tried geocoding, failed"
                continue

            print city, state

            city_pop = CityPop(city=city,
                               state=state,
                               population=population,
                               latitude=latitude,
                               longitude=longitude)

            db.session.add(city_pop)
            db.session.commit()
            total_added += 1

    print "total_added:", total_added


#######################################################################

if __name__ == "__main__":
    connect_to_db(app)
    # db.create_all()

    load_city_populations()
