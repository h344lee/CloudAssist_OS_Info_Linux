"""
input file location: 01-Adapter/logs
output file location: 00-Data Model
program location: 01-Adapter
Program name: D_CLDASST_Inventory_Reader.exe
"""

import os
import platform
import pandas as pd
import logging
import time
import datetime
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# get file names in '01-Adapter/logs' folder in a recursive way
def getInventory(current_path, current_folder, visited, file_list):

    if platform.system() == 'Windows':
        current_path = current_path + '\\' + current_folder
    else:
        current_path = current_path + '/' + current_folder

    visited[current_path] = True
    logging.debug("current path is " + current_path)
    folders = []
    current_path_files = os.listdir(current_path)
    for file_or_folder in current_path_files:
        if platform.system() == 'Windows':
            child_path = current_path + '\\' + file_or_folder
        else:
            child_path = current_path + '/' + file_or_folder

        if os.path.isdir(child_path):
            folders.append(file_or_folder)
        else:
            creation_date = time.ctime(os.path.getmtime(child_path))
            mod_date = time.ctime(os.path.getctime(child_path))
            file_owner = getOwner(child_path)

            file_list.append((current_path, file_or_folder, creation_date, mod_date, file_owner))

    for child_folder in folders:

        if platform.system() == 'Windows':
            child_path = current_path + '\\' + child_folder
        else:
            child_path = current_path + '/' + child_folder

        if visited.get(child_path) is None:
            logging.debug("go down to " + child_folder)
            getInventory(current_path, child_folder, visited, file_list)


# get file owner name. works on Windows and Linux environment
def getOwner(filename):
    username = ""
    if platform.system() == 'Windows':
        import win32security
        f = win32security.GetFileSecurity(filename, win32security.OWNER_SECURITY_INFORMATION)
        (username, domain, sid_name_use) = win32security.LookupAccountSid(None, f.GetSecurityDescriptorOwner())
        return username
    else:
        import pwd
        stat_info = os.stat(filename)
        uid = stat_info.st_uid
        username = pwd.getpwuid(uid)[0]

    return username


if __name__ == '__main__':

    logging.disable(logging.ERROR)
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s-%(levelname)s-%(message)s')
    logging.info('start of the program')

    if not os.path.isdir('logs'):
        os.makedirs('logs')
        logging.debug('"logs" folder is just created on current location.\nplease put log files in the directory')
        logging.debug('the location is ' + str(os.getcwd()) + "\\logs")
        raise Exception('please put log files in the "\\logs" folder')

    current_path = os.getcwd()
    current_folder = 'logs'
    visited = dict()
    file_list = []
    inventory_df = pd.DataFrame(columns=['FILE_ID', 'FILE_PTH', 'FILE_NM', 'FILE_SAS_SRC_CR_DT', 'FILE_SAS_SRC_CR_TM',
                                        'FILE_SAS_MOD_DT', 'FILE_SAS_MOD_TM', 'FILE_SAS_OWN'])

    # does not return a list. Instead, file_list has all the list of files as list is reference data type :)
    getInventory(current_path, current_folder, visited, file_list)

    logging.debug(file_list)

    sas_extensions = ['ddf', 'djf', 'egp', 'sas', 'sas7bcat', 'sas7bdat', 'sas7bitm', 'sc2', 'sct01', 'sd2', 'spds9',
                      'sri', 'ssd01', 'xsq']

    counter = 1
    for record in file_list:
        if record[1][-3:] in sas_extensions:

            FILE_ID = counter
            counter += 1
            FILE_PTH = record[0]+'\\'+record[1]
            FILE_NM = record[1]

            creation_time = str(datetime.datetime.strptime(record[2], "%a %b %d %H:%M:%S %Y"))

            FILE_SAS_SRC_CR_DT = creation_time[:10]
            FILE_SAS_SRC_CR_TM = creation_time[12:]

            mod_time = str(datetime.datetime.strptime(record[3], "%a %b %d %H:%M:%S %Y"))

            FILE_SAS_MOD_DT = mod_time[:10]
            FILE_SAS_MOD_TM = mod_time[12:]
            FILE_SAS_OWN = record[4]

            file_record = [FILE_ID, FILE_PTH, FILE_NM, FILE_SAS_SRC_CR_DT, FILE_SAS_SRC_CR_TM, FILE_SAS_MOD_DT,
                           FILE_SAS_MOD_TM, FILE_SAS_OWN ]
            inventory_df = inventory_df.append(pd.Series(file_record, index=inventory_df.columns), ignore_index=True)
            logging.debug(file_record)

    # get an absolute path of parent folder
    path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    # write the result to the 00-Data Model directory
    if platform.system() == 'Windows':
        if not os.path.isdir(path + "\\00-Data Model"):
            os.makedirs(path + "\\00-Data Model")
        inventory_df.to_excel(path+"\\00-Data Model\\D_CLDASST_Files_OS_Output.xlsx", index=False)
    else:
        if not os.path.isdir(path + "/00-Data Model"):
            os.makedirs(path + "/00-Data Model")
        inventory_df.to_excel(path+"/00-Data Model/D_CLDASST_Files_OS_Output.xlsx", index=False)

    logging.info('end of the program')
