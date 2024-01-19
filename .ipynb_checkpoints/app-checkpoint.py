# Import the dependencies.
import numpy as np
import flask 
print(flask.__version__)
import sqlalchemy
print(sqlalchemy.__version__)
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """These are available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    start_date_str = '2016-08-23'
    start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(and_(Measurement.date >= start_date).all())
    session.close()
    
    prcps_for_past_year = {}
    prcps_for_past_year['date'] = [row.date for row in results]
    prcps_for_past_year['precipitation'] = prcp = [row.prcp for row in results]

    return jsonify(prcps_for_past_year)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    temps_for_past_year = session.query(Measurement.tobs).filter(and_(Measurement.date >= year_ago, Measurement.date <= recent_date, Measurement.station == busiest_station)).all()
    session.close()
    return jsonify(temps_for_past_year)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    #date_str = str(start)
    #date_str = date_str.zfill(8)
    #month = date_str[:2]
    #day = date_str[2:4]
    #year = date_str[4:]
    #formatted_date = f"{year}-{month}-{day}"
    #return formatted_date

    start_query = f"""
        SELECT
                MAX(temperature) AS max_temp,
                MIN(temperature) AS min_temp,
                AVG(temperature) AS avg_temp
            FROM temperature_data
            WHERE date >= '{start}';
        """
        result = session.execute(start_query, {"start_date": start_date}).fetchone()
        if result:
            max_temp, min_temp, avg_temp = result
            print(f"Maximum Temperature: {max_temp}")
            print(f"Minimum Temperature: {min_temp}")
            print(f"Average Temperature: {avg_temp}")
        else:
            print("No temperature data found.")
    #user_number = int(input("Enter a number with this format: MMDDYYYY "))
    #formatted_date = start_date(user_number)
    #print(formatted_date)
    

if __name__ == "__main__":
    app.run(debug=True)