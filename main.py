import os
import pandas as pd

def getInventory(current_path, current_folder, visited, file_list) :
    current_path = current_path+'\\'+current_folder
    visited[current_path] = True
    print("current path is "+current_path)
    folders = []
    current_path_files = os.listdir(current_path)
    for file_or_folder in current_path_files:
        if os.path.isdir(current_path+'\\'+file_or_folder):
            folders.append(file_or_folder)
        else :
            file_list.append( (current_path, file_or_folder) )

    print("file list is" )
    for filepath, filename in file_list:
        print(filepath + " " + filename)
    print("*")*40
    for child_folder in folders:
        if visited.get(current_path+'\\'+child_folder) is None:
            print("go down to " + child_folder)
            getInventory(current_path, child_folder, visited, file_list)


def writeToExcel(file_list, inventory_df):

    file_id_num = 1
    for file_path, file_name in file_list:
        inventory_df = inventory_df.append(pd.Series([file_id_num, file_path, file_name], index=inventory_df.columns), ignore_index=True)
        file_id_num+=1
    if not os.path.isdir('output'):
        os.makedirs('output')
    inventory_df.to_excel("output\\inventory.xlsx", index=False)


if __name__ == '__main__':

    current_path = os.getcwd()
    current_folder = 'logs'
    visited = dict()
    file_list = []

    getInventory(current_path, current_folder, visited, file_list)

    print(file_list)

    inventory_df = pd.DataFrame(columns=['FILE_ID', 'FILE_PTH', 'FILE_NM'])

    writeToExcel(file_list, inventory_df)