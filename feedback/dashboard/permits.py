 # -*- coding: utf-8 -*-

import math
import datetime
import requests
import numpy as np

API_URL = 'https://opendata.miamidade.gov/resource/kw55-e2dj.json'


def api_health():
    '''
    Run the API to see if its even working.
    If it is, pass 1.
    If the county did a bad import, pass -1.
    If Socrata is down, the HTTP result code. (404, 500, etc)
    '''
    OK = 1
    COUNTY_EMPTY_DATA = -1

    r = requests.get(API_URL)
    if r.status_code == requests.codes.ok:
        json = r.json()
        if len(json[0]) == 0:
            return COUNTY_EMPTY_DATA
        else:
            return OK
    else:
        return r.status_code


def json_to_dateobj(jsondate):
    '''
    Take a string of format 2015-07-29T00:00:00 and return a datetime obj
    '''
    return datetime.datetime.strptime(jsondate, '%Y-%m-%dT%H:%M:%S')


def lifespan_api_call(arg1=0, arg2=30, property_type='c'):
    '''
    Run the API call between arg1 days ago and arg2 days ago.
    property_type should either be 'r', 'h' or 'c'. If it's an 'h',
    we take out the residential_commercial clause and we'll check
    if it's an owner/builder, if "contractor_name" = 'OWNER.'
    Defaults to 'c'
    Return the integer mean lifespan.
    If the return value is -1 the API is down.
    '''
    days_0 = (datetime.date.today() - datetime.timedelta(arg1)).strftime("%Y-%m-%d")
    days_30 = (datetime.date.today() - datetime.timedelta(arg2)).strftime("%Y-%m-%d")

    API = API_URL + '?$where=co_cc_date%20%3E=%20%27' + days_30 + '%27%20AND%20co_cc_date%20<%20%27' + days_0 + '%27%20AND%20'
    if property_type == 'h':
        API = API + 'contractor_name=%27OWNER%27'
    else:
        API = API + 'residential_commercial%20=%20%27' + property_type + '%27'
    API = API + '&$order=co_cc_date%20desc'
    response = requests.get(API)
    json_result = response.json()

    lifespan_array = []
    application_to_permit_array = []

    for resp in json_result:
        start_date = json_to_dateobj(resp['application_date'])
        permit_date = json_to_dateobj(resp['permit_issued_date'])
        end_date = json_to_dateobj(resp['co_cc_date'])

        lifespan_array.append((end_date-start_date).days)
        application_to_permit_array.append((permit_date-start_date).days)
        # permit_to_close_array.append((end_date-permit_date).days)

    result1 = np.mean(lifespan_array)
    result2 = np.mean(application_to_permit_array)

    return result1 if not math.isnan(result1) else -1, result2 if not math.isnan(result2) else -1


def get_open_permit_lifespan():
    '''
    If the return value is -1 the API is down.
    '''
    API = API_URL + '?$select=application_date&$where=co_cc_date%20IS%20NULL%20and%20master_permit_number=0'
    response = requests.get(API)
    json_result = response.json()

    today_str = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    today_obj = json_to_dateobj(today_str)

    lifespan_array = []

    for resp in json_result:
        start_date = json_to_dateobj(resp['application_date'])
        lifespan_array.append((today_obj-start_date).days)

    return int(np.mean(lifespan_array)) if not math.isnan(np.mean(lifespan_array)) else -1


def get_avg_cost(property_type='c'):
    '''
    property_type should either be 'r', 'h' or 'c'. Defaults to 'c'.
    Returns an integer. -1 if the API returns blank.
    '''
    API = API_URL + '?$select=AVG(permit_total_fee)&$where='
    if property_type == 'h':
        API = API + 'contractor_name=%27OWNER%27'
    else:
        API = API + 'residential_commercial%20=%20%27' + property_type + '%27'
    API = API + '%20and%20co_cc_date%20IS%20NULL'

    response = requests.get(API)
    result = response.json()
    try:
        result = result[0]['avg_permit_total_fee']
        return result
    except KeyError:
        return -1


def get_permit_types(arg1=0, arg2=30):
    '''
    This should print out the pie chart of all permit types.
    Defaults from 0 to 30 days but you can change it in
    arg1 and arg2. The entire JSON should be printed out
    so that the graph can be created in JS.
    '''
    days_0 = (datetime.date.today() - datetime.timedelta(arg1)).strftime("%Y-%m-%d")
    days_30 = (datetime.date.today() - datetime.timedelta(arg2)).strftime("%Y-%m-%d")

    API = API_URL + '?$select=permit_type,%20count(*)&$group=permit_type&$where=application_date%20%3E=%20%27' + days_30 + '%27%20AND%20application_date%20<%20%27' + days_0 + '%27'
    response = requests.get(API)
    json_result = response.json()
    return json_result


def get_lifespan(property_type='c'):
    '''
    property_type should either be 'r', 'h' or 'c'. Defaults to 'c'.
    Returns an object:
        val = the current lifespace
        yoy = the year over year increase or decrease (100 to -100)
    '''

    lifespan_now, waittime_now = lifespan_api_call(0, 30, property_type)

    lifespan_then, waittime_then = lifespan_api_call(30, 60, property_type)
    yoy = ((lifespan_now-lifespan_then)/lifespan_then)*100

    return {
        'val': int(lifespan_now),
        'waittime': int(waittime_now),
        'yoy': yoy
    }


def inspection_api_call(arg1=0, arg2=30):
    days_0 = (datetime.date.today() - datetime.timedelta(arg1)).strftime("%Y-%m-%d")
    days_30 = (datetime.date.today() - datetime.timedelta(arg2)).strftime("%Y-%m-%d")

    API = API_URL + '?$select=count(*)%20as%20total&$where=master_permit_number=0%20AND%20last_inspection_date%20%3E%20%27' + days_30 + '%27%20AND%20last_inspection_date%20<%20%27' + days_0 + '%27'
    response = requests.get(API)
    json_result = response.json()
    return float(json_result[0]['total'])


def get_inspection_counts():
    inspections_now = inspection_api_call(0, 30)
    inspections_then = inspection_api_call(365, 395)
    try:
        yoy = ((inspections_now-inspections_then)/inspections_then)*100
    except ZeroDivisionError:
        yoy = 0

    return {
        'val': int(inspections_now),
        'yoy': yoy
    }