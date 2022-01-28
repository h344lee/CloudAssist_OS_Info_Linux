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
            exec_date = time.ctime(os.stat(child_path).st_atime)
            file_owner = getOwner(child_path)

            file_list.append((current_path, file_or_folder, creation_date, mod_date, exec_date, file_owner))

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
    inventory_df = pd.DataFrame(columns=['INV_ID', 'INV_TYP', 'INV_LOC', 'INV_NM', 'INV_SAS_FL', 'INV_SAS_CR_DT',
                                         'INV_SAS_MD_DT', 'INV_SAS_EX_DT', 'INV_SAS_FL_OWN', 'INV_SAS_FL_MTD_LOC',
                                         'INV_SAS_FL_EXE_FLG'])

    # does not return a list. Instead, file_list has all the list of files as list is reference data type :)
    getInventory(current_path, current_folder, visited, file_list)

    logging.debug(file_list)

    sas_extensions = ['ddf', 'djf', 'egp', 'sas', 'sas7bcat', 'sas7bdat', 'sas7bitm', 'sc2', 'sct01', 'sd2', 'spds9',
                      'sri', 'ssd01', 'xsq']

    counter = 1
    for record in file_list:
        if record[1][-3:] in sas_extensions:

            INV_ID = counter
            counter += 1
            INV_TYP = ""
            INV_LOC = record[0]+'\\'+record[1]
            INV_NM = record[1]
            INV_SAS_FL = record[1]
            INV_SAS_CR_DT = record[2]
            INV_SAS_MD_DT = record[3]
            INV_SAS_EX_DT = record[4]
            INV_SAS_FL_OWN = record[5]
            INV_SAS_FL_MTD_LOC = record[0]
            if INV_SAS_EX_DT == "":
                INV_SAS_FL_EXE_FLG = 0
            else:
                INV_SAS_FL_EXE_FLG = 1

                file_record = [INV_ID, INV_TYP, INV_LOC, INV_NM, INV_SAS_FL, INV_SAS_CR_DT, INV_SAS_MD_DT, INV_SAS_EX_DT,
                               INV_SAS_FL_OWN, INV_SAS_FL_MTD_LOC, INV_SAS_FL_EXE_FLG]
                inventory_df = inventory_df.append(pd.Series(file_record, index=inventory_df.columns), ignore_index=True)
                logging.debug(file_record)

    # get an absolute path of parent folder
    path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    # write the result to the 00-Data Model directory
    if platform.system() == 'Windows':
        if not os.path.isdir(path + "\\00-Data Model"):
            os.makedirs(path + "\\00-Data Model")
        inventory_df.to_excel(path+"\\00-Data Model\\D_CLDASST_Inventory_Reader_Output.xlsx", index=False)
    else:
        if not os.path.isdir(path + "/00-Data Model"):
            os.makedirs(path + "/00-Data Model")
        inventory_df.to_excel(path+"/00-Data Model/D_CLDASST_Inventory_Reader_Output.xlsx", index=False)

    logging.info('end of the program')
