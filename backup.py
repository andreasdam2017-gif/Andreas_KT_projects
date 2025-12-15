import json
import reader
import writer
import re

def generate_backup():
    #The function sorts all the items in the inventory and writes it to a backup.txt file (Don't add any ":" in the fields)
    #Arguments : a dictionary of lists containing dictionaries
    #Returns : none
    
    #Puts all items into one list and sorts it with regard to item_id
    inventory_dict = reader.reader_system('inventory.json')
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


def swap_values_backup():
    """
    The function reads the backup file and request 3 inputs from the user.
    The first two inputs are the item ids you want to switch.
    The third input is the coloumn you want to switch as designated in the header.
    It then swaps those two values.
    There are no arguments and the function returns nothing.
    """


    # Inputs and initialization of variables
    item1 = input('Input the first item Id you want to swap : ')
    item2 = input('Input the second item Id you want to swap : ')
    backup = reader.reader_system('inventory_backup.txt')
    pattern1 = re.compile(r'^: ' + re.escape(item1))
    pattern2 = re.compile(r'^: ' + re.escape(item2))
    i = 0
    i1 = None
    i2 = None
    
    # Check if item_id exists in the backup file.
    for line in backup:
        if re.match(pattern1, line):
            i1 = i
        elif re.match(pattern2, line):
            i2 = i
        i += 1

    # If the item id does not exist it prints out which line the item does exist in.
    if i1 == None or i2 == None:
        print('one of the id\'s didn\'t exist')
        print('item1 exists in line : ',i1)
        print('item2 exists in line : ',i2)
        return
    
    # Inputs which header item you want to swap and compiles the regex that will catch the values to be swapped.
    coloumns = {'1' : 'item_name', 
                '2' : 'category', 
                '3' : 'price', 
                '4' : 'quantity_in_stock'
                }
    for i in range(1, len(coloumns)+1):
        print(f'{i} : {coloumns[str(i)]}')
    coloumn_swap = input('Which coloumn index do you want to swap? : ')
    pattern = re.compile(r'^: \d+\s*: (.+?(?=:)): ([A-Z]*[a-z]+)\s*: (\d+\.\d*)\s*: (\d+)')

    # Finds the coloumn values  and splits them into 5 groups then swaps the specified values.
    if coloumns.get(coloumn_swap):
        first_item = re.search(pattern, backup[i1])
        second_item = re.search(pattern, backup[i2])
        backup[i1] = re.sub(first_item.group(int(coloumn_swap)), second_item.group(int(coloumn_swap)), backup[i1])
        backup[i2] = re.sub(second_item.group(int(coloumn_swap)), first_item.group(int(coloumn_swap)), backup[i2])
        writer.writer_system(backup, 'inventory_backup.txt')
        #print(backup)
    else:
        print('No such index. Going back to main menue')
    



if __name__ == '__main__':
    #generate_backup()
    swap_values_backup()