import csv
import json
import os 

#We make the working directory into the file directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath) 
os.chdir(dname)
#We open the inventory.cvs file line and a new line when empty
with open("inventory.csv", newline="") as inventory:
    reader = csv.reader(inventory)
    list_dict = list(reader)

inventory_categories = {}   
inventory_list = []
#We use a for loop that creates a list of empty dictionaries, adds the key value pairs to the empty dictionaries 
for i in range(len(list_dict)-1):#-1 to remove the header in the cvs file
    inventory_list.append(dict())
    inventory_list[i].update({'item_id' : list_dict[i+1][0], 'item_name' : list_dict[i+1][1], 'category' : list_dict[i+1][2], 'price' : list_dict[i+1][3], 'quantity_in_stock' : list_dict[i+1][4]})


#We make a dictionary of categories, that sorts lists of dictionaries
#Into their respective categories
for i in range(len(inventory_list)):
    category = inventory_list[i].get('category')
    
    if category in inventory_categories:
        test = inventory_categories.get(category)
        test.append(inventory_list[i])        
        inventory_categories.update({category : test})
    else:
        emptylist = [inventory_list[i]]
        inventory_categories.update({category : emptylist})

#We open the inventory.json file and dump the dictionary of categories from above into the json file.
with open("inventory.json", mode="w") as json_dict:
    json.dump(inventory_categories, json_dict)


#We make a pretty print of the categories.     
with open("inventory.json",'r') as inventory:
    parsed = json.load(inventory)
    print(json.dumps(parsed, indent = 4))