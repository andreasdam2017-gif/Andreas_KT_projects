import json
import os
import binary_search


def reader_system(file_name):
    """
    # Function that reads a .json or .txt file
    # Argument : the file name in string format
    # returns the saved object in the file or an empty dict if it does not exist
    """
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


def writer_system(dict_of_lists, file_name):
    """
    # The function writes an object to a file
    # Arguments : object to be written to a json or txt file, the name of the file
    # Returns : nothing
    """
    if file_name.endswith('.json'):
        with open(file_name, 'w') as file:
            json.dump(dict_of_lists, file)
    elif file_name.endswith('.txt'):
        with open(file_name, 'w') as file:
            for item in dict_of_lists:
                file.writelines(f'{item}')
                

if __name__ == '__main__':
    inventory = reader_system('inventory.json')
    #print(inventory['inventory'])
    index = binary_search.BS(126, inventory['inventory'])
    if inventory['inventory'][False]:
        print(index)

