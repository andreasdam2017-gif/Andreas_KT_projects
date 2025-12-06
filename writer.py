import json


def writer_system(dict_of_lists, file_name):
    # The function writes an object to a file
    # Arguments : object to be written to a json or txt file, the name of the file
    # Returns : nothing
    if file_name.endswith('.txt'):
        with open(file_name, 'w') as file:
            json.dump(dict_of_lists, file)
    elif file_name.endswith('.txt'):
        with open(file_name, 'w') as file:
            file.write(str(dict_of_lists))
    