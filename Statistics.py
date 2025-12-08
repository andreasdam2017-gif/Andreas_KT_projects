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

    # Ensure numeric types for calculations
    df['quantity_sold'] = pd.to_numeric(df.get('quantity_sold', pd.Series(dtype='int')))  #numerics makes '20' into 20
    df['line_total'] = pd.to_numeric(df.get('line_total', pd.Series(dtype='float')))
    df['sale_id'] = pd.to_numeric(df.get('sale_id', pd.Series(dtype='int')))
    total_sales = df['line_total'].sum()
   
    #drop duplicates to count unique sales entries
    unique_sales_count = df['sale_id'].nunique()
    sales_count = df['sale_id']
    
    #Calculate average revenue per sale entry with .mean() total revenue / number of sale entries
    average_revenue_per_sale = df['line_total'].mean() if not df['line_total'].empty else 0 
    
    best_selling_by_quantity = df.groupby('item_id')['quantity_sold'].sum()
    
    best_selling_by_quantity = best_selling_by_quantity.T.sort_values(ascending=False)
    
    #print("Best selling by quantity (series):")
    #print(best_selling_by_quantity)
    print('-'* 40)
    print(f"Average revenue per sale entry: {average_revenue_per_sale}")
    print('-'* 40)
    print(f"Number of unique sales entries: {unique_sales_count}") 

    
    print('-'* 40)
    print(f"Total Revenue (sum of line_total): {total_sales}")
    print('-'* 40)

    if not best_selling_by_quantity.empty:
        most_popular_product_quantity = best_selling_by_quantity.idxmax()
        r=print("Most popular product by quantity: Item ID", most_popular_product_quantity)
    else:
        k=print("No best-selling product (no data)")
    print('-'* 40)    
        
        
        
statistics()        
    