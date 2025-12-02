import csv
import json
import os 

#We make the working directory into the file directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath) 
os.chdir(dname)
#We open the two.cvs in a try and execpt, where if error we get a empty json file.
try:
    with open("inventory.csv", newline="") as inventory: #newline if empty
        reader = csv.reader(inventory)
        list_dict = list(reader)
except:
    list_dict = []
try:   
    with open("sales.csv", newline="") as sales: #newline if empty
        reader = csv.reader(sales)
        list_dict2 = list(reader)
except:
    list_dict2=[]        
sales_list = []   
inventory_categories = {}   
inventory_list = []
#We use a for loop that creates a list of empty dictionaries, adds the key value pairs to the empty dictionaries 
for i in range(len(list_dict)-1):#-1 to remove the header in the cvs file
    inventory_list.append(dict())
    inventory_list[i].update({'item_id' : list_dict[i+1][0],
                              'item_name' : list_dict[i+1][1],
                              'category' : list_dict[i+1][2],
                              'price' : list_dict[i+1][3],
                              'quantity_in_stock' : list_dict[i+1][4]})
for i in range(len(list_dict2)-1):
    sales_list.append(dict())
    sales_list[i].update({'sale_id' : list_dict2[i+1][0],
                          'date' : list_dict2[i+1][1],
                          'item_id' : list_dict2[i+1][2],
                          'quantity_sold' : list_dict2[i+1][3],
                          'line_total' : list_dict2[i+1][4]})
sales_dict = {'sales' : sales_list}
print(sales_dict)
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

#We open both json files and dump the dictionary of categories from above into the json file.
#And also dump the sales dictionary 

with open("inventory.json", mode="w") as json_dict:
    json.dump(inventory_categories, json_dict)



with open("sales.json", mode="w") as json_dict:
    json.dump(sales_list, json_dict)

#We make a pretty print of the categories. Purely for aesthetics and easier to read   
with open("inventory.json",'r') as inventory:
    parsed = json.load(inventory)
    print(json.dumps(parsed, indent = 4))
with open("sales.json",'r') as sales:
    parsed = json.load(sales)    
    print(json.dumps(parsed, indent = 4))



    