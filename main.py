import os
import reader
from Show_sales_inventory import display
import modify_inventory
import backup
import basket_and_stats
import import_convert


# Sets the file directory to the working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath) 
os.chdir(dname)

options_menue = {'1':'Display inventory',
                 '2':'Add item to inventory',
                 '3':'Delete item from inventory',
                 '4':'Update item in inventory',
                 '5':'Register a sale',
                 '6':'Statistics on sales',
                 '7':'Generate backup from inventory',
                 '8':'Swap values in backup',
                 '9':'import test data from csv and save to json',
                 '0':'EXIT',}

options_register = {'1': display,
                    '2': modify_inventory.add_item_inventory,
                    '3': modify_inventory.delete_item_inventory,
                    '4': modify_inventory.update_inventory,
                    '5': basket_and_stats.process_sale,
                    '6': basket_and_stats.statistics,
                    '7': backup.generate_backup,
                    '8': backup.swap_values_backup,
                    '9': import_convert.import_and_convert_test_data,
                    '0': backup.generate_backup,}

back = 0

while True:
    if back == 0:
        for key, item in options_menue.items():
            print(f'{key:<2} : {item}')
        user_option = input('Choose which option you want : ')
    back = 1
    
    if user_option in options_register:
        options_register[user_option]()
        back = 0
    else:
        print('Invalid input. Try again.')
    
    break
