import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify


#Connect with data base
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Create classes
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station

# Initiate Flask 
app = Flask(__name__)


# Routes

@app.route("/")
def home():
    return (
        #List available routes
        """Available Routes:<br/><br/>
        
        /api/v1.0/precipitation<br/>
        Precipitation data by date (Last twelve months of data)<br/><br/>
        
        /api/v1.0/stations<br/>
        List of stations<br/><br/>
         
        /api/v1.0/tobs<br/>
        Temperature observations (Last twelve months of data)<br/><br/>
         
        /api/v1.0/start_date<br/>
        Type the start_date in YYYY-MM-DD format, retrieve MIN, AVG and MAX temperatures<br/><br/>
        
        /api/v1.0/start_date/end_date<br/>
        Type the start_date and end_date in YYYY-MM-DD format, retrieve MIN, AVG and MAX temperatures"""
        )


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate the date 1 year before the last date in the data
    session = Session(engine)
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year_before_last = dt.datetime.strptime(last_date[0], "%Y-%m-%d") - dt.timedelta(days=365)

    # Query for last year data
    results = session.query(measurement.date, measurement.prcp).\
                        filter(measurement.date >= year_before_last).all()

    session.close()

    # List of dicts
    precipitation = [{'date': date,
                    'prcp':prcp} for date, prcp in results]

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(station.station, station.name).all()
    
    session.close()

    stations = [{'station':station,
                'name':name} for station, name in results]
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year_before_last = dt.datetime.strptime(last_date[0], "%Y-%m-%d") - dt.timedelta(days=365)

    active_stations = session.query(measurement.station,                                 
                                func.count(measurement.station))\
                                .group_by(measurement.station)\
                                .order_by(func.count(measurement.station)\
                              .desc()).all()


    results = session.query(station.name, measurement.date, measurement.tobs).\
        filter(measurement.station == station.station).\
        filter(measurement.station == active_stations[0][0]).\
        filter(measurement.date >= year_before_last).all()

    session.close()


    tobsl = [{'name':name,
            'date':date,
            'tobs':tobs} for name, date, tobs in results]
    
    return jsonify(tobsl)


@app.route("/api/v1.0/<start>")
def start_date(start):
    start_date = start.split("-")
    start_date = dt.date(int(start_date[0]), int(start_date[1]), int(start_date[2]))   
    
    session = Session(engine)
    
    results = session.query(measurement.date,\
                            func.min(measurement.tobs),\
                            func.avg(measurement.tobs),\
                            func.max(measurement.tobs)).\
                filter(measurement.date >= start_date).\
                group_by(measurement.date).all()
        
    session.close()

    temperatures = [{'date':date,
                    'min':tmin,
                    'avg':tavg,
                    'max':tmax} for date, tmin, tavg, tmax in results]
    
    return jsonify(temperatures) 


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    start_date = start.split("-")
    end_date = end.split("-")
    
    start_date = dt.date(int(start_date[0]), int(start_date[1]), int(start_date[2]))   
    end_date = dt.date(int(end_date[0]), int(end_date[1]), int(end_date[2]))   
    
    session = Session(engine)
    
    results = session.query(measurement.date,\
                            func.min(measurement.tobs),\
                            func.avg(measurement.tobs),\
                            func.max(measurement.tobs)).\
            filter(measurement.date >= start_date).\
            filter(measurement.date <= end_date).\
            group_by(measurement.date).all()
        
    session.close()


    temperatures = [{'date':date,
                    'min':tmin,
                    'avg':tavg,
                    'max':tmax} for date, tmin, tavg, tmax in results]
    
    return jsonify(temperatures) 

        

if __name__ == '__main__':
    app.run(debug=True)
    #app.run()