import json
import multiprocessing
import math
import logging
from elasticsearch import Elasticsearch
from elasticsearch import helpers

from xxx_capacity_format_conflict import xxx_capacity_format_conflict
from xxx_xxxType_outlines_conflict import xxx_xxxType_outlines_conflict
from xxx_location_format_conflict import xxx_location_format_conflict
from xxx_type_format_conflict import xxx_type_format_conflict
from xxx_paytype_format_conflict import xxx_paytype_format_conflict
from xxx_price_schema_conflict import xxx_price_schema_conflict

from general_address_format_conflict import general_address_format_conflict
from general_opening_time_format_conflict import general_opening_time_format_conflict
from general_condition_conflict import general_condition_conflict
from general_id_format_conflict import general_id_format_conflict
from general_others_conflict import general_others_conflict
from general_poi_format_conflict import general_poi_format_conflict
from general_name_format_conflict import general_name_format_conflict
from general_version_format_conflict import general_version_format_conflict

from charging_fee_conflict import charging_fee_conflict

from ***_price_format_extract import ***_price_format_extract
from ***_opening_hour_string_extract import ***_opening_hour_string_extract
from ***_rate_desc_extract import ***_rate_desc_extract
from ***_groundType_extract import ***_groundType_extract

xxx_index_name = "***_xxx_domain"
xxx_doc_type_name = "***_xxx_domain_info"
charging_index_name = "***_charging_domain"
charging_doc_type_name = "***_charging_domain_info"
cpu_num = multiprocessing.cpu_count()


def process_xxx_data(data, data_type, filter_class):

    x = general_address_format_conflict(data, data_type)
    x = general_id_format_conflict(x, data_type)
    x = general_opening_time_format_conflict(x, data_type)
    x = general_name_format_conflict(x, data_type)
    x = general_poi_format_conflict(x, data_type)
    x = general_condition_conflict(x, data_type)
    x = general_others_conflict(x, data_type)

    # add version control for the second layer
    x = general_version_format_conflict(x, data_type)

    # add xxx logic
    x = xxx_capacity_format_conflict(x, data_type)
    x = xxx_price_schema_conflict(x, data_type)
    x = xxx_xxxType_outlines_conflict(x, data_type)
    x = xxx_location_format_conflict(x, data_type)
    x = xxx_type_format_conflict(x, data_type)
    x = xxx_paytype_format_conflict(x, data_type)

    # add *** ETL tool
    x = ***_price_format_extract(x)
    x = ***_opening_hour_string_extract(x)
    x = ***_rate_desc_extract(x)
    x = ***_groundType_extract(x)

    if filter_class.filter(x) is False:
        input_data = {
            "MAID": x["***"]["MAID"],
            "originalID": x["***"]["originalID"],
        }

        # save general data
        es_client.index(
            index=xxx_index_name,
            doc_type=xxx_doc_type_name,
            body=input_data
        )
        print("send data successfully! %s" % x["***"]["MAID"])


def process_charging_data(data, data_type, filter_class):
    x = general_address_format_conflict(data, data_type)
    x = general_id_format_conflict(x, data_type)
    x = general_opening_time_format_conflict(x, data_type)
    x = general_name_format_conflict(x, data_type)
    x = general_poi_format_conflict(x, data_type)
    x = general_condition_conflict(x, data_type)
    x = general_others_conflict(x, data_type)

    if data_type != "AMAP":
        # add charging fee format reconstructure
        x = charging_fee_conflict(x, data_type)

    # add version control logic for the second layer
    x = general_version_format_conflict(x, data_type)

    if filter_class.filter(x) is False:
        input_data = {
            "MAID": x["***"]["MAID"],
            "originalID": x["***"]["originalID"],
            "equipmentInfos": [],
        }
        if "EquipmentInfos" in x:
            count = 0
            for equips in x["EquipmentInfos"]:
                input_data["equipmentInfos"].append({
                    "equipmentID": equips["EquipmentID"],
                })
                for connector in equips["ConnectorInfos"]:
                    input_data["equipmentInfos"][count]["connectorInfos"].append({
                        "connectorID": connector["ConnectorID"],
                    })
                count += 1

        # save general data
        try:
            es_client.index(
                index=charging_index_name,
                doc_type=charging_doc_type_name,
                body=input_data
            )
            print("send data successfully! %s" % x["***"]["MAID"])
        except:
            print(input_data)
            raise Exception("error happened")


class xxxFilter(object):

    maid_list = set()

    def __init__(self, es_client):
        result = helpers.scan(
            index=xxx_index_name,
            doc_type=xxx_doc_type_name,
            client=es_client,
            _source=["MAID"],
            query={"query": {"match_all": {}}},
            scroll="3m"
        )
        for item in result:
            self.maid_list.add(item['_source']["MAID"])

    def filter(self, data):
        """
        Return True means the data needs to be filtered, false means the data will store into ES
        :param data:
        :return:
        """
        # filter all the contained MAID
        if data["***"]["MAID"] in self.maid_list:
            return True

        # filter all the data without "lon", "lat"
        if data["***"]["location"]["lat"] is None or \
            data["***"]["location"]["lon"] is None:
            return True

        # self defined filter function
        if data["***"]["cityName"] == "--" and \
                (data["***"]["source"] == "--" or data["***"][
                    "source"] == "--"):
            return True
        else:
            return False


class ChargingFilter(object):

    maid_list = set()

    def __init__(self, es_client):
        result = helpers.scan(
            index=charging_index_name,
            doc_type=charging_doc_type_name,
            client=es_client,
            _source=["MAID"],
            query={"query": {"match_all": {}}},
            scroll="3m"
        )
        for item in result:
            self.maid_list.add(item['_source']["MAID"])

    def filter(self, data):
        """
        Return True means the data needs to be filtered, false means the data will store into ES
        :param data:
        :return:
        """
        # filter all the contained MAID
        if data["***"]["MAID"] in self.maid_list:
            return True

        # filter all the data without "lon", "lat"
        if data["***"]["location"]["lat"] is None or \
                data["***"]["location"]["lon"] is None:
            return True

        return False


def data_distributor(input_data):
    chunk, data_type, index_type, filter_class = input_data
    for data in chunk:
        if index_type.lower() == "xxx":
            process_xxx_data(data, data_type, filter_class)
        else:
            process_charging_data(data, data_type, filter_class)


def task_distributor(data, data_type, index_type, filter_class):
    # 1. divide the data into several parts
    parts = cpu_num
    data_num = len(data)
    chunks = []

    print("start to divide data")
    for i in range(parts):
        start_point = math.floor(i * data_num / parts)
        end_point = math.floor((i + 1) * data_num / parts)
        chunks.append((data[start_point:end_point], data_type, index_type, filter_class))

    # 2. start several process
    print("start to process data")
    pool = multiprocessing.Pool(processes=cpu_num)
    pool.map(data_distributor, chunks)


if __name__ == "__main__":
    es_client = Elasticsearch([{"host": "", "port": }])
    charging_content_type = [
        #
    ]
    charging_files = [
        #
    ]
    xxx_content_type = [
        #
    ]
    xxx_files = [
        #
    ]
    index_type = [
        #
    ]

    # initial filter class to do filtring
    xxx_filter = xxxFilter(es_client)
    charging_filter = ChargingFilter(es_client)

    # DO charging calculation
    for i in range(len(charging_content_type)):
        print("start to save %s charging data" % charging_content_type[i])
        data = json.load(open(charging_files[i], "r"))
        task_distributor(data, charging_content_type[i], index_type[0], charging_filter)

    # DO xxx calculation
    for i in range(len(charging_content_type)):
        print("start to save %s xxx data" % xxx_content_type[i])
        data = json.load(open(xxx_files[i], "r"))
        task_distributor(data, xxx_content_type[i], index_type[1], xxx_filter)