import os
import reader
from Show_sales_inventory import display
import modify_inventory
import backup
import basket


# Sets the file directory to the working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath) 
os.chdir(dname)

options_menue = {'1':'Display inventory',
                 '2':'Display sales',
                 '3':'Add item to inventory',
                 '4':'Delete item from inventory',
                 '5':'Update item in inventory',
                 '6':'Register a sale',
                 '7':'Statistics on sales',
                 '8':'Generate backup from inventory',
                 '9':'Swap values in backup',
                 '10':'import test data from csv and save to json',
                 '0':'EXIT',}

options_register = {'1': display,
                    '2': display,
                    '3': modify_inventory.add_item_inventory,
                    '4': modify_inventory.delete_item_inventory,
                    '5': modify_inventory.update_inventory,
                    '6':'Register a sale',
                    '7':'Statistics on sales',
                    '8': backup.generate_backup,
                    '9': backup.swap_values_backup,
                    '10':'import test data from csv and save to json',
                    '0': backup.generate_backup,}

while True:
    for key, item in options_menue.items():
        print(f'{key:<2} : {item}')


    break
