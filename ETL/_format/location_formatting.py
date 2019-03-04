import logging
from logging.config import fileConfig
import os

def parking_location_formatting(data, type):
    
    result=[]
    fileConfig(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) +
               "/logging_config.ini", disable_existing_loggers=False)
    logger = logging.getLogger("ETL_tool")
	
    if type.lower() in [,,,]:
        if type == '':

            num = len(data['***']['locationPoint']['locationType'])
            if num > 0:
                for i in range(num):
                    try:
                        lon = float(data['***']['locationPoint']['location']['lon'][i])
                        lat = float(data['***']['locationPoint']['location']['lat'][i])
                        eetype = data['***']['locationPoint']['locationType'][i]
                        locationType = eetype.replace('出入口','entrance/exit').replace('出口','exit').replace('入口','entrance')
                        pointID = data['***']['locationPoint']['pointID'][i]
                        gridCode = data['***']['locationPoint']['gridCode']
                        pointName = data['***']['locationPoint']['pointName'] + eetype
                        result.append({'location':{'lat': lat,'lon':lon},'locationType': locationType, 'pointID': pointID,'gridCode':gridCode,'pointName':pointName})                 
                    except KeyError as e:
                        logger.warning('invalid key: '+str(e))
                    
        if type == '':

            for i in range(2):
                try:
                    if data['***']['locationPoint']['location']['lon'][i] != "":
                        lon = float(data['***']['locationPoint']['location']['lon'][i])
                        lat = float(data['***']['locationPoint']['location']['lat'][i])
                        eetype = "入口" if i==0 else "出口"
                        locationType = eetype.replace('出口','exit').replace('入口','entrance')
                        pointID = data['***']['locationPoint']['pointID']+"-"+str(len(result)+1)
                        gridCode = data['***']['locationPoint']['gridCode']
                        pointName = data['***']['locationPoint']['pointName'] + eetype
                        result.append({'location':{'lat': lat,'lon':lon},'locationType': locationType, 'pointID': pointID,'gridCode':gridCode,'pointName':pointName})                 
                except KeyError as e:
                    logger.warning('invalid key: '+str(e))
                    
    else:
        logger.error('unexpected data source {}'.format(type))
       
    data['***']['locationPoint']=result   
    return data


if __name__ == "__main__":
    # show the example data
    integrated_data = {
        #
    }

    # this is the format after data integration
    formatted_format = {
        #
    }

    result = parking_location_formatting(integrated_data, "")
    print(result)