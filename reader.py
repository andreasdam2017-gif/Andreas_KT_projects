import json
import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath) 
os.chdir(dname)


def reader_userinput(directory):
    # The function lists json files in the working directory and loads the chosen file.
    # Arguments : directory = working directory
    # Returns : The chosen json file 
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                print(file)
    file_to_be_loaded = input('From the listed files which one do you want to load? : ')
    try:
        with open(file_to_be_loaded, 'r') as file:
            loaded_file = json.load(file)
    except:
        loaded_file = {'':[]}
    return loaded_file


def reader_system(file_name):
    try:
        if file_name.endswith('.json'):
            with open(file_name, 'r') as file:
                loaded_file = json.load(file)
            return loaded_file
        elif file_name.endswith('.txt'):
            with open(file_name, 'r') as file:
                return file.readlines()
    except:
        return {}