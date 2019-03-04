
import sys
sys.path.append('..')

from kodai_opening_hour_string_extract import *
import numpy as np
import hashlib

#unit test for POF-2
def test_kodai_opening_hour_string_extract():
    
     #1. Test a normal example
     time_structure = {'time':[{'days': 127,
                        'season': 15,
                        'timeRange': [{'from': '10:00', 'to': '24:00'}]}],
                        'timeText': '周一至周日\n10:00-24:00'}
     input1 = {'generatedAttributes':{'openingHours':time_structure},'kodaiAttributes':{}}
     output1 = kodai_opening_hour_string_extract(input1)
     assert output1['kodaiAttributes']['openingHours'] == str(time_structure)
     #2. Test the abnormal examples
     #2.1 One of the input is null
    
     input2 = {'generatedAttributes':{'openingHours':time_structure}}
     output2 = kodai_opening_hour_string_extract(input2)
     assert output2['kodaiAttributes']['openingHours'] == str(time_structure)
     
     #2.2 The input is Null
     input3 = {'generatedAttributes': {}}
     output3 = kodai_opening_hour_string_extract(input3)
     assert output3 == None

     #2.3 The input is None
     input4 = None
     output4 = kodai_opening_hour_string_extract(input4)
     assert output4 == None
     
     
     
     
     
     