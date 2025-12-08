import json
import reader
import writer

def generate_backup(inventory_dict):
    #The function sorts all the items in the inventory and writes it to a backup.txt file (Don't add any ":" in the fields)
    #Arguments : a dictionary of lists containing dictionaries
    #Returns : none
    
    #Puts all items into one list and sorts it with regard to item_id
    backup_li = []
    for keys, category in inventory_dict.items():               #Pointer pointing to the category list
        backup_li += category
    backup_li = sorted(backup_li, key=lambda x: x['item_id'])
    
    #Opens the backup file and assigns the keys to a variable
    backup_file = open('inventory_backup.txt', 'w')
    backup_keys = backup_li[0].keys()
    
    #Prints the header to the bakup file
    for key in backup_keys:
        backup_file.writelines(f': {key:<{len(key)+10}}')
    backup_file.writelines(f'\n')
    for key in backup_keys:
        backup_file.writelines(f'{"-"*(len(key)+10)}')
    backup_file.writelines(f'\n')

    #Prints the items to the backup file and closes it
    for i in range(len(backup_li)):
        for key, value in backup_li[i].items():
            backup_file.writelines(f': {value:<{len(key)+10}}')
        backup_file.writelines(f'\n')
    backup_file.close()


if __name__ == '__main__':
    inventorydict = reader.reader_system('inventory.json')
    generate_backup(inventorydict)