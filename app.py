import pandas as pd
import numpy as np
import os
import sqlalchemy
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Text, Float
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import matplotlib.pyplot as plt
from flask import Flask, jsonify
import json


engine = create_engine("sqlite:///hawaii.sqlite")
conn = engine.connect()

Base= automap_base()
Base.prepare(engine,reflect=True)
Base.classes.keys()
inspector=inspect(engine)
inspector.get_table_names()
inspector.get_columns("measurements")
inspector.get_columns("stations")

class Measurements(Base):
    __tablename__ = "measurements"
    __table_args__ = {"extend_existing":True}
    mes_id = Column(Text,primary_key=True)

class Stations(Base):
    __tablename__ = "stations"
    __table_args__ = {"extend_existing":True}
    station = Column(Text,primary_key=True)

Base.prepare()
session=Session(engine)

app = Flask(__name__)
@app.route("/")
def homepage():
    return(
        f"Kyrus Wankadiya - Week 11 HW Flask Application</br></br></br>"
        f"List of possible urls:</br></br>"
        f"HOME PAGE:</br>/</br></br>"
        f"STATION LIST:</br>/api/v1.0/stations</br></br>"
        f"PRECIPITATION HISTORY:</br>/api/v1.0/precip</br></br>"
        f"OBSERVED TEMPERATURE HISTORY:</br>/api/v1.0/tobs</br></br>"
        f"TEMP START DATE ONLY:</br>/api/v1.0/YYYY-MM-DD</br></br>"
        f"TEMP START & END DATE:</br>/api/v1.0/YYYY-MM-DD/YYYY-MM-DD</br></br>")

@app.route("/api/v1.0/precip")
def precip():
    meslist = []
    output = session.query(Measurements).filter(Measurements.date>"2016-08-23")
    for row in output:
        meslist.append([row.station,row.date,row.prcp])
    mesdataframe = pd.DataFrame(meslist,columns=["station","date","prcp"]).set_index(["station","date"]).unstack()
    mestodict = mesdataframe["prcp"].T.fillna(0).to_dict()
    return(jsonify(mestodict))

@app.route("/api/v1.0/stations")
def stations():
    sta_dict = {}
    output = session.query(Stations)
    for row in output:
        sta_dict[row.station] = row.name
    return(jsonify(sta_dict))

@app.route("/api/v1.0/tobs")
def tobs():
    toblist = []
    output = session.query(Measurements).filter(Measurements.date>"2016-08-23")
    for row in output:
        toblist.append([row.station,row.date,row.tobs])
    tobdataframe = pd.DataFrame(toblist,columns=["station","date","tobs"]).set_index(["station","date"]).unstack()
    tobtodict = tobdataframe["tobs"].T.fillna(0).to_dict()
    return(jsonify(tobtodict))    

@app.route("/api/v1.0/<startdate>")
@app.route("/api/v1.0/<startdate>/<enddate>")
def startend(startdate,enddate=""):
    selist = []
    if enddate=="":
        output = session.query(Measurements).filter(Measurements.date>=str(startdate))
    else:
        output = session.query(Measurements).filter(Measurements.date.between(str(startdate),str(enddate)))
    for row in output:
        selist.append(int(row.tobs))
    sedict = {}
    sedict["TMIN"] = min(selist)
    sedict["TAVG"] = np.mean(selist)
    sedict["TMAX"] = max(selist)
    return(jsonify(sedict))

if __name__ == "__main__":
    app.run(debug=True)

