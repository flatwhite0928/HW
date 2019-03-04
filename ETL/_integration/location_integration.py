
# coding: utf-8


import configparser as cp
import logging
from logging.config import fileConfig
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+ "/util")

from relation_util import *

def parking_location_integration(data, type, config):
    # 1. create a empty dictionary or a None variable
    result = {
        "locationPoint": {
            "location": {
                "lat": None,
                "lon": None
            },
            "gridCode": "",
            "locationType": "",
            "pointID": "",    
            "pointName": ""
        }
    }
         
    fileConfig(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) +
               "/logging_config.ini", disable_existing_loggers=False)
    logger = logging.getLogger("ETL_tool")
    
    # 2. get the name of the attribute we want to get
    if type.lower() in [,,,]:
        
        if type.lower() == "":
            lon_name = config["locationPoint.location.lon"][type.lower()]
            lon_name_path = lon_name.split(",")
            print(lon_name_path)
            lon_data = []
            for path in lon_name_path:
                if path!="":
                    try:
                        lon_data.append(data[path.strip()])
                except KeyError as e:
                    logger.warning('invalid key: '+str(e))
        else:    
            try:
                lon_data = fetch(data, config["locationPoint.location.lon"][type.lower()])
            except:
                lon_data = None
            
        if type.lower() == "":
            lat_name = config["locationPoint.location.lat"][type.lower()]
            lat_name_path = lat_name.strip().split(",")
            lat_data = []
            for path in lat_name_path:
                if path !="":
                    try:
                        lat_data.append(data[path.strip()])
                except KeyError as e:
                    logger.warning('invalid key: '+str(e))
        else:    
            try:
                lat_data = fetch(data, config["locationPoint.location.lat"][type.lower()])
            except:
                lat_data = None
            
        gridCode_name = config["locationPoint.gridCode"][type.lower()]
        
        try:
            locationType_name = fetch(data, config["locationPoint.locationType"][type.lower()])
        except:
            locationType_name = ""
            
        try: 
            pointID_name = fetch(data, config["locationPoint.pointID"][type.lower()])
        except:
            pointID_name = ""
            
        pointName_name = config["locationPoint.pointName"][type.lower()]
        
        # 3. get the attribute from a nested object
        gridCode_name_path = gridCode_name.split(".")
        gridCode_data = result["locationPoint"]["gridCode"]
        for path in gridCode_name_path:
            if path !="":
                try:
                    gridCode_data = data[path]
                except KeyError as e:
                    logger.warning('invalid key: '+str(e))
                
        pointName_name_path = pointName_name.split(".")
        pointName_data = result["locationPoint"]["pointName"]
        for path in pointName_name_path:
            if path !="":
                try:
                    pointName_data = data[path]
                except KeyError as e:
                    logger.warning('invalid key: '+str(e))

        # 4. put into result
        result["locationPoint"]["location"]["lon"] = lon_data
        result["locationPoint"]["location"]["lat"] = lat_data
        result["locationPoint"]["gridCode"] = gridCode_data
        result["locationPoint"]["locationType"] = locationType_name
        result["locationPoint"]["pointID"] = pointID_name
        result["locationPoint"]["pointName"] = pointName_data
    
    else:

        logger.error('unexpected data source {}'.format(type))
    # 5. put into raw data
    if "generatedAttributes" not in data:
        data["generatedAttributes"] = {}

    data["generatedAttributes"] = result

    return data


if __name__ == "__main__":
    # show the example data
    data = {
        #
    }

    # this is the format after data integration
    integrate_format = {
        #
    }     


    parser = cp.ConfigParser()
    # os.path.dirname is to get parent dir
    parser.read(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/relationship_base/parking_location_format_conflict.ini")
    result = parking_location_integration(data, "etcp", parser)
    print(result)