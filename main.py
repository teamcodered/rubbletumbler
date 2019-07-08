from rubbletumbler.net import  download_files, download_file, url_parts, root_content_dl_addr, get_csv_file_contents, get_csv_file_data, get_matching_files
import argparse
import re
import os
import sys
import datetime

fname = 'MOD03.A2019176.2225.061.NRT.hdf'

def browse_action(args):
    if args.list:
        ctr = 0
        for url in list(url_parts.keys()):
            print('[{0}]\t{1}'.format(ctr, url_parts[url][0]))
            ctr += 1

    else:
        repo_index = 0
        day = 100

        if args.day:
            day = args.day

        if args.index:
            repo_index = args.index

        repoKey = list(url_parts.keys())[repo_index]
        csv_file_contents = get_csv_file_contents(repoKey)
        # print(csv_file_contents)
        print(repoKey)
        
        if args.day:
            day_url = root_content_dl_addr + csv_file_contents[str(day)] + '?fields=all&format=csv'
            day_csv_data = get_csv_file_data(day_url)   
            print('Day ' + str(args.day))
            # print(day_csv_data)
            file_to_loc  = { t[5]: t[1] for t in day_csv_data }
            if args.start_time and args.end_time:
                start_tm = args.start_time
                end_tm = args.end_time
            
                matching_files = get_matching_files(file_to_loc, start_tm, end_tm)
                print('Matching files: for start time {0}, end time {1} \n'.format(start_tm, end_tm))
                for k,v in matching_files.items():
                    print('{0}\t{1}'.format(k,v))
                #[print('{0}\t{1}'.format(k,v)) for k,v in matching_files.items()]
                if args.download:
                    download_dest = args.download
                    for k,v in matching_files.items():
                        download_file(v, k, download_dest)
            else:
                # print all files in day folder
                [print('{0}\t{1}'.format(k,v)) for k,v in file_to_loc.items()]
                # print(file_to_loc)
                if args.download:
                    download_dest = args.download
                    for k,v in file_to_loc.items():
                        download_file(v, k, download_dest)

            # check for download
            


        else:            
            for k,v in csv_file_contents.items():
                print('{0}\t{1}'.format(k,v))
            

def download_action(args):

    # download hdf files        
    dest_dir = './dump'

    start_dt = datetime.datetime.today()
    start_dt = start_dt.replace(hour= 0, minute = 0)
    end_dt = datetime.datetime.today()
    end_dt = end_dt.replace(hour = 23, minute = 59)
    
    start_tm = datetime.datetime.now().replace( hour= 0, minute = 0)
    end_tm = datetime.datetime.now().replace(hour = 23, minute = 59)
    
    selected_repo_idx = 0

    if args.index:
        selected_repo_idx = args.index

    '''
    if args.start_date:
        start_dt = datetime.datetime.strptime(args.start_date, '%Y%d%mT%H%M')

    if args.end_date:
        end_dt = datetime.datetime.strptime(args.end_date, '%Y%d%mT%H%M')
    '''
    if args.start_time:
        start_tm = datetime.datetime.strptime(args.start_time, '%H:%M')

    if args.end_time:
        end_tm = datetime.datetime.strptime(args.end_time, '%H:%M')

    if args.path:
        if not os.path.isdir(args.path):
            os.mkdir(args.path)
            dest_dir = args.path
    #print('start date: {0}\nend date: {1}\noutput folder: {2}\n'.format(start_dt, end_dt, dest_dir))
    print('start time: {0}\nend time: {1}\noutput folder: {2}\n'.format(start_tm, end_tm, dest_dir))       
    print("downloading ...\n")
    selected_repo_key = list(url_parts.keys())[selected_repo_idx]
    # download_files(selected_repo_key, dest_dir, start_dt, end_dt)
    csv_file_contents = get_csv_file_contents(selected_repo_key)
    print(csv_file_contents)

    print(args)    
    

def save_action(args):
    print("saving ...\n")
    print(args)    

parser = argparse.ArgumentParser(prog = 'rubbletumbler', description = 'Retrieve and import data from an Earthdata repository into a database.')
subparser = parser.add_subparsers(title = "Tasks", description = 'specify a task for rubbletumbler to perform', required = True)
download_parser = subparser.add_parser('download', help = "download HDF data from repository")
save_parser = subparser.add_parser('save', help = 'save HDF data to database')

''' Use the browser parser to allow the user browse available files on the remote repository '''
browse_parser = subparser.add_parser('browse', help = 'browse available files on remote repository')
mex = browse_parser.add_mutually_exclusive_group()

mex.add_argument('-l','--list', action='store_const', const=1, metavar='list', help = 'list available repositories')

remote_actions_group = mex.add_argument_group()
remote_actions_group.add_argument('-i', '--index', help = 'index of remote repository', type = int)
remote_actions_group.add_argument('-d', '--day', help='day of year', type = int)
remote_actions_group.add_argument('-st','--start-time', metavar='start_time', help = 'hh:mm start time', type = str)
remote_actions_group.add_argument('-et','--end-time', metavar = 'end_time', help = 'hh:mm end time', type = str)
remote_actions_group.add_argument('-dl','--download', help = 'download matching files into target directory', type = str)

browse_parser.set_defaults(func = browse_action)
#mex = download_parser.add_mutually_exclusive_group()

#date_selection_group = mex.add_argument_group()
#date_selection_group.add_argument('-sd','--start-date', metavar='startdate', help = 'start date', type = str)
#date_selection_group.add_argument('-ed','--end-date', metavar='enddate', help = 'end date', type = str)
#mex.add_argument_group(time_selection_group)

#download_parser.add_argument('path', metavar='path', help = 'destination directory to dump files')

time_selection_group = download_parser.add_argument_group()
time_selection_group.add_argument('-i','--index',metavar = 'index', help = 'index of selected repository', type = int)
time_selection_group.add_argument('path', metavar='path', help = 'destination directory to dump files')
time_selection_group.add_argument('-st','--start-time', metavar='start_time', help = 'hh:mm start time', type = str)
time_selection_group.add_argument('-et','--end-time', metavar = 'end_time', help = 'hh:mm end time', type = str)

download_parser.set_defaults(func = download_action)

save_parser.add_argument('-u', '--url', help = 'url of target database')
save_parser.add_argument('-un', '--username', help = 'username for target database')
save_parser.add_argument('-p', '--password', help = 'password for target database')
save_parser.add_argument('-d', '--directory', help = 'source folder')
save_parser.set_defaults(func = save_action)

args = parser.parse_args()
args.func(args)
# print(args)
# print(args.Tasks)
# first_url = list(url_parts.keys())[0]
# print(first_url)
# download_csv(first_url)