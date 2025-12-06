import json
import os
import reader
import writer
# Set working directory to the script's directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
def process_sale():
    sales_data = reader.reader_system('sales.json')
    # Normalize sales_data: support either a dict wrapper or a plain list
    if isinstance(sales_data, dict):
        sales_list = sales_data.get("sales", [])
    else:
        sales_list = sales_data
    
    for n,k in sales_list:
        print(f"sale_id: {k['sale_id']}, Quantity_Sold: {k['quantity_sold']}")
        print(n)
        key = k['sale_id']
        quantity = k['quantity_sold']
    
    print(key)    
        
process_sale()        
    