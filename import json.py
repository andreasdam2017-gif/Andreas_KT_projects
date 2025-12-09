import json
import os
import reader
import writer
import numpy as np
import pandas as pd
sales_data = reader.reader_system('sales.json')
inventory_categories = reader.reader_system('inventory.json')
sales_stats = pd.json_normalize(sales_data, record_path=['sales'])#To remove the nested dict
#flattens the inventory Dictionary so it becomes a single dictionary
inventory_categories = [item for category_list in inventory_categories.values() for item in category_list]
    
inventory_stats = pd.json_normalize(inventory_categories) #Now we can normalise
print(inventory_stats)
print(sales_stats)