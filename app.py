# Import the dependencies.
import numpy as np
import flask 
print(flask.__version__)
import sqlalchemy
print(sqlalchemy.__version__)
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date(YYYY-mm-dd)<br/>"
        f"/api/v1.0/start_date(YYYY-mm-dd)/end_date(YYYY-mm-dd)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    start_date_str = '2016-08-23'
    start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= start_date).all()
    session.close()
    
    prcps_for_past_year = {}
    prcps_for_past_year['date'] = [row.date for row in results]
    prcps_for_past_year['precipitation'] = [row.prcp for row in results]
    prcps_for_past_year_tuple = list(zip(prcps_for_past_year['date'], prcps_for_past_year['precipitation']))


    return jsonify(prcps_for_past_year_tuple)

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
    active_station = 'USC00519281'
    start_date_str = '2016-08-23'
    start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(and_(Measurement.station == active_station, Measurement.date >= start_date)).all()
    session.close()

    busiest_for_past_year = {}
    busiest_for_past_year['date'] = [row.date for row in results]
    busiest_for_past_year['temperature'] = [row.tobs for row in results]
    busiest_for_past_year_tuple = list(zip(busiest_for_past_year['date'], busiest_for_past_year['temperature']))
    
    return jsonify(busiest_for_past_year_tuple)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)

    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()

    result = session.query(
        func.max(Measurement.tobs).label('max_temp'),
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp')
    ).filter(Measurement.date >= start_date).first()

    session.close()

    if result:
        max_temp, min_temp, avg_temp = result
        response = {
            "Maximum Temperature": max_temp,
            "Minimum Temperature": min_temp,
            "Average Temperature": avg_temp
        }
        return jsonify(response)
    else:
        return jsonify({"error": "No temperature data found."})
    
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)

    start_time = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end_time = dt.datetime.strptime(end, "%Y-%m-%d").date()

    result = session.query(
        func.max(Measurement.tobs).label('max_temp'),
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp')
    ).filter(and_(Measurement.date >= start_time, Measurement.date <= end_time)).first()

    session.close()

    if result:
        max_temp, min_temp, avg_temp = result
        response = {
            "Maximum Temperature": max_temp,
            "Minimum Temperature": min_temp,
            "Average Temperature": avg_temp
        }
        return jsonify(response)
    else:
        return jsonify({"error": "No temperature data found."})

if __name__ == "__main__":
    app.run(debug=True)