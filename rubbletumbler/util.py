import pathlib
import os
import datetime

''' Date utilites
'''

def convert_date_to_doy(input_date):
    ''' Converts a date to day of year format 
    Params:
        input_date: input date string in yyyy-mm-dd format
    Returns: int - the given date in day of year
    '''
    dt = datetime.datetime.strptime(input_date, '%Y-%m-%d')
    return dt.timetuple.tm_yday    
    

def convert_doy_to_date(doy):
    ''' Gets the date object for a given day-of-year value
    Params:
        doy: string yyyy-doy value e.g 2019-180
    Returns:
        date: a date object for the supplied value
    '''
    dt = datetime.datetime.strptime(doy, '%Y-%j')
    return dt
    


''' A dataset is a folder that contains a collection of HDF data. The structure is defined by the path to the folder
and range of dates for the data
'''
class Dataset:
    def __init__(self, path, start_date, end_date):
        self.path = path
        self.start_date = start_date
        self.end_date = end_date


''' A factory method that generates a dataset from an existing folder '''
def dataset_from_folder(path):
    pass
