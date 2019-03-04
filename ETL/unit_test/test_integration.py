import json
from parking_capacity_format_conflict import parking_capacity_format_conflict
from parking_parkingType_outlines_conflict import parking_parkingType_outlines_conflict
from parking_location_format_conflict import parking_location_format_conflict
from parking_type_format_conflict import parking_type_format_conflict
from parking_paytype_format_conflict import parking_paytype_format_conflict
from parking_price_schema_conflict import parking_price_schema_conflict
from parking_parkAndRide_conflict import parking_parkAndRide_conflict
from parking_image_conflict import parking_image_conflict
from parking_restriction_conflict import parking_restriction_conflict
from parking_rating_conflict import parking_rating_conflict

from general_address_format_conflict import general_address_format_conflict
from general_opening_time_format_conflict import general_opening_time_format_conflict
from general_avgRating_format_conflict import general_avgRating_format_conflict
from general_condition_conflict import general_condition_conflict
from general_id_format_conflict import general_id_format_conflict
from general_others_conflict import general_others_conflict
from general_poi_format_conflict import general_poi_format_conflict
from general_name_format_conflict import general_name_format_conflict
from general_version_format_conflict import general_version_format_conflict

from charging_fee_conflict import charging_fee_conflict


def test_0_schema_integration_test():
    content_type = []
    files = [""]
    result_data = []
    for i in range(len(content_type)):
        test_type = content_type[i]
        test_data = json.load(open("/***/%s.json" % files[i], "r"))
        for data in test_data:
            x = parking_capacity_format_conflict(data, test_type)
            x = parking_parkingType_outlines_conflict(x, test_type)
            x = parking_location_format_conflict(x, test_type)
            x = parking_type_format_conflict(x, test_type)
            x = parking_paytype_format_conflict(x, test_type)
            x = parking_price_schema_conflict(x, test_type)
            x = parking_parkAndRide_conflict(x, test_type)
            x = parking_image_conflict(x, test_type)
            x = parking_restriction_conflict(x, test_type)
            x = parking_rating_conflict(x, test_type)
            result_data.append(x)

    for data in result_data:
        # start to test realtime attribute
        assert "realTime" in list(data["***"].keys())
        assert "capacityStatus" in list(data["***"]["realTime"].keys())
        assert "availableNum" in list(data["***"]["realTime"].keys())
        assert "probeTime" in list(data["***"]["realTime"].keys())
        assert "state" in list(data["***"]["realTime"].keys())
        assert "trend" in list(data["***"]["realTime"].keys())
        assert "probability" in list(data["***"]["realTime"].keys())

        # start to test outlines attribute
        assert "outlines" in list(data["***"].keys())
        if len(list(data["***"]["outlines"])) > 0:
            assert "outlinesID" in list(data["***"]["outlines"][0].keys())
            assert "subShortName" in list(data["***"]["outlines"][0].keys())
            assert "outlinesType" in list(data["***"]["outlines"][0].keys())
            assert "coordinates" in list(data["***"]["outlines"][0].keys())
            assert "outlinesParkingType" in list(data["***"]["outlines"][0].keys())
            assert "outlinesSurfaceType" in list(data["***"]["outlines"][0].keys())

        # start to test locationPoint attribute
        assert "locationPoint" in list(data["***"].keys())
        if len(list(data["***"]["locationPoint"])) > 0:
            assert "pointID" in list(data["***"]["locationPoint"][0].keys())
            assert "pointName" in list(data["***"]["locationPoint"][0].keys())
            assert "locationType" in list(data["***"]["locationPoint"][0].keys())
            assert "location" in list(data["***"]["locationPoint"][0].keys())
            assert "gridCode" in list(data["***"]["locationPoint"][0].keys())

        # start to test features
        assert "parkingFeatures" in list(data["***"].keys())
        assert "brakeType" in list(data["***"].keys())
        assert "parkAttribute" in list(data["***"].keys())
        assert "totalChargePlace" in list(data["***"].keys())
        assert "totalParkPlace" in list(data["***"].keys())

        # test paytype attributes
        assert "paymentCashType" in list(data["***"].keys())
        assert "paymentLocationType" in list(data["***"].keys())

        # test *chema attributes
        assert "*Schema" in list(data["***"].keys())
        assert "avgCostPrecise" in list(data["***"]["*Schema"].keys())
        assert "policies" in list(data["***"]["*Schema"].keys())
        assert "*" in list(data["***"]["*Schema"].keys())
        if len(list(data["***"]["*Schema"]["*"])) > 0:
            assert "times" in list(data["***"]["*Schema"]["*"][0].keys())
            assert "days" in list(data["***"]["*Schema"]["*"][0]["times"].keys())
            assert "from" in list(data["***"]["*Schema"]["*"][0]["times"].keys())
            assert "to" in list(data["***"]["*Schema"]["*"][0]["times"].keys())
            assert "currency" in list(data["***"]["*Schema"]["*"][0].keys())
            assert "currencyCode" in list(data["***"]["*Schema"]["*"][0].keys())
            assert "maxStayMinutes" in list(data["***"]["*Schema"]["*"][0].keys())
            assert "carClass" in list(data["***"]["*Schema"]["*"][0].keys())
            assert "costs" in list(data["***"]["*Schema"]["*"][0].keys())
            if len(list(data["***"]["*Schema"]["*"][0]["costs"])) > 0:
                assert "amount" in list(data["***"]["*Schema"]["*"][0]["costs"][0].keys())
                assert "amountRounded" in list(data["***"]["*Schema"]["*"][0]["costs"][0].keys())
                assert "during" in list(data["***"]["*Schema"]["*"][0]["costs"][0].keys())
                assert "duringText" in list(data["***"]["*Schema"]["*"][0]["costs"][0].keys())
                assert "text" in list(data["***"]["*Schema"]["*"][0]["costs"][0].keys())
                assert "args" in list(data["***"]["*Schema"]["*"][0]["costs"][0].keys())


        # test parkAndRide attributes
        assert "parkAndRide" in list(data["***"].keys())

        # test image attributes
        assert "images" in list(data["***"].keys())
        if len(list(data["***"].keys())) > 0:
            assert "typeID" in list(data["***"]["images"][0].keys())
            assert "photoType" in list(data["***"]["images"][0].keys())
            assert "photoID" in list(data["***"]["images"][0].keys())
            assert "url" in list(data["***"]["images"][0].keys())

        # test restriction attributes
        assert "usageRestriction" in list(data["***"].keys())
        assert "maxHeight" in list(data["***"].keys())
        assert "heightRestrictFlag" in list(data["***"].keys())

        # test rating attributes
        assert "rating" in list(data["***"].keys())
        assert "score" in list(data["***"]["rating"].keys())
        assert "numreviews" in list(data["***"]["rating"].keys())
        assert "numvotes" in list(data["***"]["rating"].keys())


def test_charging_schema_integration_test():
    content_type = [""]
    files = [
        
    ]
    result_data = []
    for i in range(len(content_type)):
        test_type = content_type[i]
        test_data = json.load(open("/***/%s.json" % files[i], "r"))
        for data in test_data:
            x = charging_fee_conflict(data, test_type)
            result_data.append(x)

        for data in result_data:
            # start to test fee format
            assert "electricityFee" in list(data["***"].keys())
            assert "parkFee" in list(data["***"].keys())
            assert "serviceFee" in list(data["***"].keys())

