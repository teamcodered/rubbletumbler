import requests
import csv
import re
import datetime
import time
import os

import urllib.request

base_url = 'https://nrt3.modaps.eosdis.nasa.gov/archive/allData/61'
root_content_dl_addr = 'https://nrt3.modaps.eosdis.nasa.gov'
csv_file_name = 'files.csv'
app_key = '084070F0-9DDC-11E9-9B4A-716545326583'

url_parts = {
    'geo-5min-swath-1km': ('Geolocation, 5-min swath 1km','MOD03','https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/details/allData/61/MOD03/2019?fields=all&format=csv'),
    'l2-temp-h2o-vapor-profiles-5min': ('L2 Temperature and Water Vapor Profiles, 5-Min Swath 5km', 'MOD07_L2', 'https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/details/allData/61/MOD07_L2/2019?fields=all&format=csv'),
    'l2-total-ppt-h2o-5': ('L2 Total Precipitable Water Vapor, 5-Min Swath 1km and 5km', 'MOD05_L2','https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/details/allData/61/MOD05_L2/2019?fields=all&format=csv'),
    'l2-thermal-anomalies': ('L2 Thermal Anomalies / Fire, 5-Min Swath 1km','MOD14','https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/details/allData/6/MOD14/2019?fields=all&format=csv'),
    'l2-surface-temp': ('L2 Surface Temperature and Emissivity, 5-Min Swath 1km','MOD11_L2', 'https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/details/allData/6/MOD11_L2/2019?fields=all&format=csv'),

    'l2-thermal-anomalies':('L2 Thermal Anomalies / Fire, 5-Min Swath 1km', 'MYD14', 'https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/details/allData/6/MYD14/2019?fields=all&format=csv'),
    'l2-surface-reflectance':('L2 Surface Reflectance, 5-Min Swath 250m, 500m, and 1km','MYD09','https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/details/allData/6/MYD09/2019?fields=all&format=csv'),
    'l2-surface-temp-2':('L2 Surface Temperature and Emissivity, 5-Min Swath 1km','MYD11_L2', 'https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/details/allData/6/MYD11_L2/2019?fields=all&format=csv'),
    'l2-daytime-geo-angles':('L2G Daytime Geolocation Angles, Daily 1km','MYDMGGAD', 'https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/details/allData/6/MYDMGGAD/2019?fields=all&format=csv')
}

def get_csv_file_data(url: str):
    ''' get available files from csv file
    Params:
        url: a string containing the url for the repository
    Returns: a list of tuples containing the csv file contents
         
    '''
    result = []
    csv_url = None
    with requests.get(url, stream = True, headers = { 'Authorization': 'Bearer ' + app_key }) as r:
        r.raise_for_status()
        with open(csv_file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size = 8192):
                if chunk:
                    f.write(chunk)   
            f.close()     

    # finished writing. read file.
    with open(csv_file_name, 'r') as f:

        csv_reader = csv.reader(f, delimiter = ',')
        line_count = 0
        for row in csv_reader:
            # print(row)
            line_count += 1
            # skip first line - it should be the csv file header
            if line_count == 1: 
                continue
            #content_file_name = row[5]
            #content_file_path = row[6]
            #result[content_file_name] = content_file_path
            line = []
            for r in row:
                line.append(r)
            result.append(line)
    return result


def get_csv_file_contents(url_part_key):
    ''' get available files from csv file
    Params:
        url_part_key: a key specifying the key for the selected repository
    Returns: a dictionary containing the links to the HDF files in a given repository
         
    '''
    result = {}
    csv_url = url_parts[url_part_key][2]
    with requests.get(csv_url, stream = True, headers = { 'Authorization': 'Bearer ' + app_key }) as r:
        r.raise_for_status()
        with open(csv_file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size = 8192):
                if chunk:
                    f.write(chunk)   
            f.close()     

    # finished writing. read file.
    with open(csv_file_name, 'r') as f:

        csv_reader = csv.reader(f, delimiter = ',')
        line_count = 0
        for row in csv_reader:
            # print(row)
            line_count += 1
            # skip first line - it should be the csv file header
            if line_count == 1: 
                continue
            content_file_name = row[5]
            content_file_path = row[6]
            result[content_file_name] = content_file_path

    return result

def get_matching_files(file_contents_struct, start_time, end_time):
    # todo: move to utils
    ''' Gets all the files that match a given time window
    Params:
        file_contents_struct: a dict containing file name to path mappings
        start_time: hh:mm a time specifying the start time for the time window
        end_time: hh:mm a time specifying the end time for the time window
    Returns:
        A list containing only files matching the required time window
    '''
    matching_files = {}
    
    for k, v in file_contents_struct.items():
        pat =  r'\w+\.A(\d+)\.(\d+)\.\w+\.\w+\.hdf';
        match = re.search(pat, k)
        match_yd, match_hm = match.group(1), match.group(2)
        match_hm_t = time.strptime(match_hm, '%H%M')
        date_tm = datetime.datetime.strptime(match_yd+'T'+match_hm, "%Y%jT%H%M")
        #print('match_hm_t = ' + str(match_hm_t))
        start_time_t = time.strptime(start_time, '%H:%M')
        end_time_t = time.strptime(end_time, '%H:%M')
        if match_hm_t >= start_time_t and match_hm_t <= end_time_t:
            # match found
            matching_files[k] = v
    return matching_files

def download_file(download_url, file_name, output_dir):
    ''' Download a file from the repository into the output directory
    '''
    if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'Bearer ' + app_key)]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(root_content_dl_addr + download_url, output_dir + file_name)
    '''
    with requests.Session() as session:
        with session.get(root_content_dl_addr + download_url, stream = True, headers = { 'Authorization': 'Bearer: ' + app_key}) as r:
            r.raise_for_status()        
            with open(os.path.join(output_dir, file_name), 'wb') as f:
                for chunk in r.iter_content(chunk_size = 8192):
                    if chunk:
                        f.write(chunk)
                f.close() 
    '''

def download_files(url_part_key, output_folder_path, start_date, end_date):
    csv_url = url_parts[url_part_key][2]    
    with requests.get(csv_url, stream = True, headers = { 'Authorization': 'Bearer ' + app_key }) as r:
        r.raise_for_status()
        with open(csv_file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size = 8192):
                if chunk:
                    f.write(chunk)   
            f.close()     

        # finished writing. read file.
        with open(csv_file_name, 'r') as f:

            csv_reader = csv.reader(f, delimiter = ',')
            line_count = 0
            for row in csv_reader:
                print(row)
                line_count += 1
                # skip first line - it should be the csv file header
                if line_count == 1: 
                    continue
                content_file_name = row[5]
                content_file_path = row[6]
                print(str.format('Analysing content file name: {0}, content file path:{1}', content_file_name, content_file_path))
                pat =  r'\w+\.A(\d+)\.(\d+)\.\w+\.\w+\.hdf';
                match = re.search(pat, content_file_name)
                match_yd, match_hm = match.group(1), match.group(2)
                print(str.format('Found file with date: {0}, time: {1}', match_yd, match_hm))
                entry_date = datetime.datetime.strptime(match_yd + 'T' + match_hm, "%Y%jT%H%M")
                print(str.format('Found entry: {0}', entry_date))

                if entry_date > start_date and entry_date < end_date:
                    print('entry {0} matched time window: {1} - {2}'.format(entry_date, start_date, end_date))
                    downloadLink = root_content_dl_addr + content_file_path
                    with requests.get(downloadLink, stream = True, headers = {'Authorization': 'Bearer ' + app_key}) as r:
                        r.raise_for_status()
                        with open(os.path.join(output_folder_path, content_file_name)) as f:
                            for chunk in r.iter_content(chunk_size = 8192):
                                if chunk:
                                    f.write(chunk)
                        print('downloaded: {0}'.format(content_file_name))
                else:
                    print('date {0} did not match.'.format(entry_date))
            
                #TODO: Add logging
