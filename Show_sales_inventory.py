import json
import csv
import os
#We make the working directory into the file directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath) 
os.chdir(dname)

with open("inventory.json", "r") as f:
    inventory_categories = json.load(f)
with open("sales.json", "r") as f:
    sales_dict = json.load(f)
#print it out in a readable way
print("Inventory Categories:")
print("-" * 100)    
for category, items in inventory_categories.items():    
    print(f"\nCategory: {category}")
     
    for item in items:
        print(f"  \nItem ID: {item['item_id']} \nName: {item['item_name']} \nPrice: {item['price']} \nQuantity in Stock: {item['quantity_in_stock']}")
    print("-" * 100)     
    

    

   
    