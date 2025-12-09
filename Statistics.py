import json
import os
import reader
import writer
import numpy as np
import pandas as pd #Panda is good for data frames and statistics
# Set working directory to the script's directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
def statistics():
    sales_data = reader.reader_system('sales.json')
    
    # Normalize sales data: support either {'sales': [...]} or a plain list of sale dicts
    if isinstance(sales_data, dict) and 'sales' in sales_data:
        sales_stats = pd.json_normalize(sales_data['sales'])
    elif isinstance(sales_data, list):
        sales_stats = pd.json_normalize(sales_data)
    else:
        # empty or unexpected format, makes it into an empty DataFrame
        sales_stats = pd.DataFrame()
  
    df = sales_stats
    if df.empty:
        print("No sales data available to compute statistics.")
        return

     # Convert columns (that hold numbers as strings) to real numeric types so you can do math on them  
    df['quantity_sold'] = pd.to_numeric(df.get('quantity_sold', pd.Series(dtype='int')))  #numerics makes '20' into 20
    df['line_total'] = pd.to_numeric(df.get('line_total', pd.Series(dtype='float')))
    df['sale_id'] = pd.to_numeric(df.get('sale_id', pd.Series(dtype='int')))
    
    total_sales = df['line_total'].sum()
   
    #drop duplicates to count unique sales entries
    unique_sales_count = df['sale_id'].nunique()
    sales_count = df['sale_id']
    
  # average revenue per sale entry (i.e. average of line_total per row)
    average_revenue_per_sale = df['line_total'].mean() if not df['line_total'].empty else 0 #looks if line_total is empty
    # mean() computes the average of the line_total column
    
    best_selling_by_quantity = df.groupby('item_id')['quantity_sold'].sum()
    print('Sales Statistics:')    
    print('-' * 40)
    print(f'Average revenue per sale entry: {average_revenue_per_sale}')
    print('-' * 40)
    print(f'Number of unique sales entries: {unique_sales_count}') 
    
    print('-' * 40)
    print(f'Total Revenue (sum of line_total): {total_sales}')
    print('-' * 40)

    
        # idxmax(): finds the index (item_id) of the max value in the series or the item with highest total quantity sold
    most_popular_product_quantity = best_selling_by_quantity.idxmax()
    print('Most popular product by quantity: Item ID', most_popular_product_quantity)

    print('-' * 40)   
    r = (input('If you wish to see a record of all sales, press 1'))
    if r == '1':
        (print(df.to_string())) #.to_string() is to prevent truncation
        
        
        
statistics()        
    