import os
import platform
import pandas as pd
import logging
import time
import win32security


def getInventory(current_path, current_folder, visited, file_list):
    current_path = current_path + '\\' + current_folder
    visited[current_path] = True
    logging.debug("current path is " + current_path)
    folders = []
    current_path_files = os.listdir(current_path)
    for file_or_folder in current_path_files:
        if os.path.isdir(current_path + '\\' + file_or_folder):
            folders.append(file_or_folder)
        else:
            file_path = current_path + '\\' + file_or_folder
            creation_date = time.ctime(os.path.getmtime(file_path))
            mod_date = time.ctime(os.path.getctime(file_path))
            exec_date = time.ctime(os.stat(file_path).st_atime)
            file_owner = GetOwner(file_path)

            file_list.append((current_path, file_or_folder, creation_date, mod_date, exec_date, file_owner))

    for child_folder in folders:
        if visited.get(current_path + '\\' + child_folder) is None:
            logging.debug("go down to " + child_folder)
            getInventory(current_path, child_folder, visited, file_list)


def GetOwner(filename):

    username = ""
    if platform.system() == 'Windows':
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

    logging.disable(logging.DEBUG)
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

    getInventory(current_path, current_folder, visited, file_list)

    logging.debug(file_list)

    for number, record in enumerate(file_list):

        INV_ID = number+1
        INV_TYP = ""
        INV_LOC = record[0]+'\\'+record[1]
        INV_NM = record[1]
        INV_SAS_FL = record[1]
        INV_SAS_CR_DT = record[2]
        INV_SAS_MD_DT = record[3]
        INV_SAS_EX_DT = record[4]
        INV_SAS_FL_OWN = record[5]
        INV_SAS_FL_MTD_LOC = record[0]
        INV_SAS_FL_EXE_FLG = ""

        file_record = [INV_ID, INV_TYP, INV_LOC, INV_NM, INV_SAS_FL, INV_SAS_CR_DT, INV_SAS_MD_DT, INV_SAS_EX_DT,
                       INV_SAS_FL_OWN, INV_SAS_FL_MTD_LOC, INV_SAS_FL_EXE_FLG]

        inventory_df = inventory_df.append(pd.Series(file_record, index=inventory_df.columns), ignore_index=True)

    if not os.path.isdir('output'):
        os.makedirs('output')
    inventory_df.to_excel("output\\inventory.xlsx", index=False)

    logging.info('end of the program')
