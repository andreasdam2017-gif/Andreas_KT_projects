import json
import os
import tempfile


def writer_system(dict_of_lists, file_name):
    # The function writes an object to a file
    # Arguments : object to be written to a json or txt file, the name of the file
    # Returns : nothing
    if file_name.endswith('.json'):
        with open(file_name, 'w') as file:
            json.dump(dict_of_lists, file)
    elif file_name.endswith('.txt'):
        with open(file_name, 'w') as file:
            for item in dict_of_lists:
                file.writelines(f'{item}')