import json
import os
import reader
import writer
from datetime import datetime, timedelta
import numpy as np
 

# Set working directory to the script's directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def process_sale():

    sales_data = reader.reader_system('sales.json')
    inventory_categories = reader.reader_system('inventory.json')



    # Determine the next sale_id by examining existing sales
    # Normalize sales_data: support either a dict  or a plain list
    if isinstance(sales_data, dict): #isinstance checks if its a dict or something else and returns boolean true or false
        sales_list = sales_data.get('sales', [])
    else:
        sales_list = sales_data
     
    if sales_data == {} or inventory_categories == {}:
        print('Empty Sales or Inventory Dictionary, cannot continue.')
        return

    # We'll compute next_key when a sale starts (so each sale gets a fresh id or continue having the old one)

    # Outer loop: allow starting multiple sales until the user exits
    new_customer = 0
    while True:
        try:
            ask = int(input('Would you like to purchase something? Press 1 to buy and anything else to cancel: '))
                    
        except ValueError:#Incase user writes a non interger
            print('Invalid input — cancelling.')            
            break

        if ask != 1:
            print('Purchase cancelled.')            
            break
        if new_customer == 1:
            verify = int(input('Are you a new customer or do you wish to buy more as the same customer? Press 1 if new or Press 2 to continue shopping:  '))
        
        # Initialize next_key based on customer type
        next_key = None
        if new_customer == 0 or verify == 1:
            # Compute next sale_id for this new sale (fresh id per sale)
            max_id_str = max(sales_list, key=lambda s: int(s['sale_id']))['sale_id'] #using lamba function to get the max sale_id instead of a loop
            next_key = str(int(max_id_str) + 1)
        elif verify == 2:
            # Keeps same sale_id but allows you to buy more
            max_id_str = max(sales_list, key=lambda s: int(s['sale_id']))['sale_id']
            next_key = str(int(max_id_str))
        else:
            print('Invalid choice. Please enter 1 or 2.')
            continue
                
        # use today's date. Expected stored date format is YYYY-MM-DD.
        if sales_list:            
            date = datetime.now().strftime("%Y-%m-%d")                

 
        
        # Show available categories
        for category in inventory_categories.keys():
            print(f"  {category}")
        user_cat = input('What Category? (type Dairy to get Dairy products): ').strip()

        if user_cat in inventory_categories:
            items = inventory_categories[user_cat]
            print(f'\nItems in {user_cat}:')
            for item in items:
                print(f'  ID: {item["item_id"]} - Name: {item["item_name"]} - Qty: {item["quantity_in_stock"]}')

            user_item_id = input('What Item ID do you want?:  ').strip()
            # Create mapping item_id
            item_dict = {item['item_id']: item for item in items}
            result = item_dict.get(user_item_id)

            if result:
                print(f'You selected: {result}')

                qty = int(result['quantity_in_stock'])
                try:
                    user_qty = int(input('How much do you want?:  '))
                except ValueError:
                    print('Invalid input, try again')
                    continue

                if user_qty <= 0 or user_qty != int(user_qty): #Makes sure user cant buy negative or non interger amounts
                    print('Invalid quantity requested.')
                    continue
                
                if user_qty <= qty:  # Check stock before allowing the sale
                    sold_qty = user_qty
                    new_qty = qty - user_qty
                    result['quantity_in_stock'] = str(new_qty)
                    print(f'Remaining quantity: {new_qty}')
                    # Compute sale line details (price and line total)
                    price = float(result['price'])
                    line_total = price * user_qty  # Total revenue for this line
                    new_sale = {
                        'sale_id': next_key,
                        'date': date,
                        'item_id': result['item_id'],
                        'quantity_sold': sold_qty,
                        'line_total': str(line_total)
                    }

                    # Append the sale line to sales_list and update lookup
                    sales_list.append(new_sale)                 

                    writer.writer_system(sales_list, 'sales.json')

                    print('Added sale:', new_sale)
                    # show total number of sale lines 
                    print('Total number of sale lines now:', len(sales_list))
                    new_customer = 1

                    writer.writer_system(inventory_categories, 'inventory.json')  # updates inventory after sale been concluded
                else:
                    print(f'Not enough stock. Available: {qty}, Requested: {user_qty}')
            else:
                print(f'No item found with ID {user_item_id}')
        else:
            print(f'Category {user_cat} not found')



def statistics():
    sales_data = reader.reader_system('sales.json')

    
    if isinstance(sales_data, dict) and 'sales' in sales_data:
        sales_list = sales_data['sales']
    elif isinstance(sales_data, list):
        sales_list = sales_data
    else:
        print('No sales data available to compute statistics.')
        return

    if not sales_list:
        print('No sales data available to compute statistics.')
        return

    # Extract columns into NumPy arrays
    sale_id = np.array([int(s['sale_id']) for s in sales_list])
    item_id = np.array([int(s['item_id']) for s in sales_list])
    quantity_sold = np.array([int(s['quantity_sold']) for s in sales_list])
    line_total = np.array([float(s['line_total']) for s in sales_list])

    

    total_sales = np.sum(line_total)

    unique_sales_count = len(np.unique(sale_id))

    average_revenue_per_sale = np.mean(line_total) if line_total.size > 0 else 0

    # Group by item_id and sum quantity_sold
    unique_items = np.unique(item_id)
    total_quantity_per_item = {
        item: quantity_sold[item_id == item].sum()
        for item in unique_items
    }

    # Find item with max quantity sold
    most_popular_product_quantity = max(
        total_quantity_per_item,
        key=total_quantity_per_item.get
    )

    
    print('Sales Statistics:')
    print('-' * 40)
    print(f'Average revenue per sale entry: {average_revenue_per_sale:.2f}')
    print('-' * 40)
    print(f'Number of unique sales entries: {unique_sales_count}')
    print('-' * 40)
    print(f'Total Revenue (sum of line_total): {total_sales:.2f}')
    print('-' * 40)
    print('Most popular product by quantity: Item ID', most_popular_product_quantity)
    print('-' * 40)


if __name__ == "__main__":
    statistics()


