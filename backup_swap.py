import reader
import writer
import re

def swap_values_backup():



    #Inputs and initialization of variables
    item1 = input('Input the first item Id you want to swap : ')
    item2 = input('Input the second item Id you want to swap : ')
    backup = reader.reader_system('inventory_backup.txt')
    pattern1 = re.compile(r'^: ' + re.escape(item1))
    pattern2 = re.compile(r'^: ' + re.escape(item2))
    i = 0
    i1 = None
    i2 = None
    
    #Check if item_id exists in the backup file.
    for line in backup:
        if re.match(pattern1, line):
            i1 = i
        elif re.match(pattern2, line):
            i2 = i
        i += 1

    #If the item id does not exist it prints out which line the item does exist in.
    if i1 == None or i2 == None:
        print('one of the id\'s didn\'t exist')
        print('item1 exists in line : ',i1)
        print('item2 exists in line : ',i2)
        return
    
    #Inputs which header item you want to swap and compiles the regex that will catch the values to be swapped.
    coloumn_swap = input('Which coloumn value do you want to swap? : ')
    coloumns = {'item_id' : 1
                , 'item_name' : 2
                , 'category' : 3
                , 'price' : 4
                , 'quantity_in_stock' : 5}
    pattern = re.compile(r'^: (\d+)\s*: (.+?(?=:)): ([A-Z]*[a-z]+)\s*: (\d+\.\d*)\s*: (\d+)')

    #finds the coloumn values  and splits them into 5 groups then swaps the specified values.
    if coloumns[coloumn_swap]:
        first_item = re.search(pattern, backup[i1])
        second_item = re.search(pattern, backup[i2])
        backup[i1] = re.sub(first_item.group(coloumns[coloumn_swap]), second_item.group(coloumns[coloumn_swap]), backup[i1])
        backup[i2] = re.sub(second_item.group(coloumns[coloumn_swap]), first_item.group(coloumns[coloumn_swap]), backup[i2])
        writer.writer_system(backup, 'inventory_backup.txt')
        #print(backup)

    

#For testing the funciton
if __name__ == '__main__':
    swap_values_backup()