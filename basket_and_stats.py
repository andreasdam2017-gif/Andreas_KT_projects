import json
import os
import reader_writer
from datetime import datetime, timedelta
import numpy as np
import binary_search




def process_sale():
    """
    Processes the sale of a customer, correctly gives a customer a sale_id and removes stocks in inventory.json
    and updates sales_json with a new sale_ID and sales, it then updates the inventory with new stocks.
    it loops until user leaves at the beginning of each sale.
    This function doesnt return any values, just records new sale and updates the inventory.
    """

    sales_dict = reader_writer.reader_system('sales.json')
    inventory_dict = reader_writer.reader_system('inventory.json')
    
    # Determine the next sale_id by examining existing sales
    # Normalize sales_dict: support either a dict  or a plain list
    if isinstance(sales_dict, dict):
        sales_list = sales_dict.get('sales', [])
    else:
        sales_list = sales_dict
    
    if isinstance(inventory_dict, dict):
        inventory = inventory_dict.get('inventory', [])
    else:
        inventory = inventory_dict

    if not sales_list or not inventory:
        print('Empty Sales or Inventory data, cannot continue.')
        input('Going back to main menu, press enter to confirm')
        return

    inventory_storage = inventory
    # Group inventory by category so it becomes a nesteed dict
    grouped = {}

    for item in inventory:
        if "category" not in item:
            continue

        category = item["category"]

        if category not in grouped:
            grouped[category] = []

        grouped[category].append(item)

    categories = sorted(grouped.keys())     

    new_customer = 0
   # Purchase loop 
    while True:
        #intialising variables
        index = 0
        item = 0
        qty = 0
        result = 0
        user_item_id = 0
        user_qty = 0
        selected = 0
        choice = 0
        try:
            ask = int(input(
                'Would you like to purchase something? Press 1 to buy and anything else to cancel: '
            ))
        except ValueError:
            print('Invalid input — cancelling.')
            break

        if ask != 1:
            print('Purchase cancelled.')
            break

       
        verify = 1
        if new_customer == 1:
            verify = int(input('Press 1 for new customer or 2 to continue shopping: ' ))

        # Determine sale_id
        if new_customer == 0 or verify == 1:
            max_id_str = max(sales_list, key=lambda s: int(s['sale_id']))['sale_id']
            next_key = str(int(max_id_str) + 1)
        elif verify == 2:
            max_id_str = max(sales_list, key=lambda s: int(s['sale_id']))['sale_id']
            next_key = str(int(max_id_str))
        else:
            print('Invalid choice.')
            continue

        date = datetime.now().strftime("%Y-%m-%d")

        # Show categories
        print("\nAvailable categories:\n")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")

        choice = input('\nChoose a category number: ')

        if not choice.isdigit():
            print('Invalid input, expected interger.')
            continue

        index = int(choice) - 1

        if index < 0 or index >= len(categories):
            print('Choice out of range.')
            continue

        selected = categories[index]
        print(f"\nItems in {selected}:\n")
        for item in grouped[selected]:
            print(
            f"ID: {item.get('item_id')} - "
            f"{item.get('item_name', 'No name')} | "
            f"Available: {item.get('quantity_in_stock')}"
    )
        
        user_item_id = input('\nEnter item ID: ').strip()
        try:
            result = binary_search.BS(int(user_item_id), grouped[selected])                          
                
        except ValueError:
            print('Invalid input, expected interger')
            continue
        
        if result < 0:
            print('Item_ID not found')
            continue
            
  
        item = grouped[selected][result] 

        qty = int(item['quantity_in_stock'])

        try:
            user_qty = int(input('How much do you want?: '))
        except ValueError:
            print('Invalid input, expected interger value.')
            continue

        if user_qty <= 0:
            print('Invalid quantity requested.')
            continue

        if user_qty > qty:
            print(f'Not enough stock. Available: {qty}')
            continue

        # Update inventory
        item['quantity_in_stock'] = str(qty - user_qty)
        sold_qty = user_qty
        

        price = float(item['price'])
        line_total = price * user_qty
        inv_price = str(price)

        new_sale = {
            'sale_id': next_key,
            'date': date,
            'item_id': item['item_id'],
            'quantity_sold': sold_qty,
            'line_total': f'{line_total:.2f}'
        }
                
        sales_list.append(new_sale) 

        reader_writer.writer_system(sales_dict, 'sales.json')        
        reader_writer.writer_system(inventory_dict, 'inventory.json')

        print('Added sale:', new_sale)
        print('Total sale lines:', len(sales_list))
        item_ID_verify = 0
        item = 0
        new_customer = 1


def statistics():
    """
    This function checks if there exist statistics to show, then sorts the sales data into numpy arrays and calcluates it 
    and prints the appropriate stats. 
    
    The Function doesnt return any values.
    """
    sales_dict = reader_writer.reader_system('sales.json')

    
    if isinstance(sales_dict, dict) and 'sales' in sales_dict:
        sales_list = sales_dict['sales']
    elif isinstance(sales_dict, list):
        sales_list = sales_dict
    else:
        print('No sales data available to compute! statistics!.')
        input('Going back to main menu, press enter to confirm')
        return

    if not sales_list:
        print('No sales data available to compute statistics.')
        input('Going back to main menu, press enter to confirm')
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
    input('Going back to main menu, press enter to confirm')


if __name__ == "__main__":
    statistics()
    process_sale()