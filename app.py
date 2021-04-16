import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
base = automap_base()

# Reflect the tables 
base.prepare(engine,reflect=True)

# Save references to each table
Measurement = base.classes.measurement
Station = base.classes.station

# Flask
app = Flask(__name__)

# Flask Routes
#List all routes that are available
@app.route("/")
def Home():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (ex:2010-01-01)<br/> "
        f"/api/v1.0/start/end (ex:2010-01-01/2011-01-01)<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of query results using date as the key and prcp as value"""
    session = Session(engine)
    # Find the most recent date in the data set.
    # most_recent = session.query(Measurement.date).order_by(Measurement.date).first()

    # Calculate the date one year from the last date in data set.
    prior_year = dt.date(2010,1,1) - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    data_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prior_year).all()

    session.close()
    precip_score = []
    for i, prcp in data_query:
        data_query = {}
        data_query['date'] = i
        data_query['prcp'] = prcp
        precip_score.append(data_query)

    return jsonify(precip_score)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    session = Session(engine)
    data = session.query(Station.name, Station.station, Station.elevation).all()
    session.close()
    #create dictionary for JSON
    stations_list = []
    for i in data:
        row = {}
        row['name'] = i[0]
        row['stations'] = i[1]
        row['elevation'] = i[2]
        stations_list.append(row)
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point for the most active station."""
    session = Session(engine)
    prior_year = dt.date(2010,1,1) - dt.timedelta(days=366)
    data_query = session.query(Station.name,Measurement.date, Measurement.tobs).filter(Measurement.date >= prior_year).\
        filter(Measurement.station == 'USC00519281').\
            filter(Measurement.station == Station.station).all()
    session.close()

    # Use dictionary to create json
    temps_list = []
    for i in data_query:
        row = {}
        row["Date"] = i[1]
        row["Station"] = i[0]
        row["Temperature"] = int(i[2])
        temps_list.append(row)

    return jsonify(temps_list)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    session = Session(engine)
    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                               func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    session.close()
    list1 = []
    for i in from_start:
        row = {}
        row["Date"] = i[0]
        row["Min Temp"] = i[1]
        row["Avg Temp"] = i[2]
        row["Max Temp"] = i[3]
        list1.append(row)

    return jsonify(list1)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    session = Session(engine)
    ranges = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                           func.max(Measurement.tobs)).filter(Measurement.date >= start).\
                           filter(Measurement.date <= end).group_by(Measurement.date).all()
    session.close()
    list1 = []
    for i in ranges:
        row = {}
        row["Date"] = i[0]
        row["Min Temp"] = i[1]
        row["Avg Temp"] = i[2]
        row["Max Temp"] = i[3]
        list1.append(row)

    return jsonify(list1)

if __name__ == '__main__':
    app.run(debug=True)
