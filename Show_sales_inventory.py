import json
import csv
import os
import reader

#We make the working directory into the file directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath) 
os.chdir(dname)


#print it out in a readable way

def display(display_file):
    #This functions accepts dictionaries and displays the content of said dictionary in a readable way. It does not return any
    #Value, but just displays the content.
    display_items = reader.reader_system(display_file)
    for cate_name, items in display_items.items():#We take the outer dict and display its name in a for loop
        print()
        print('-' * 40)
        print(f'Category: {cate_name}')     
        for index, item in enumerate(items, start=1):#We make an enumerate in the inner dict in the nested loop so that we can,
            print(f'  Item {index}:')                #find its index in the list
            for key, value in item.items():          #We print the key and values in the index
                print(f'    {key} = {value}')
                
display('inventory.json')#Change name if you wish to see inventory.json or sales.json file

    

   
    