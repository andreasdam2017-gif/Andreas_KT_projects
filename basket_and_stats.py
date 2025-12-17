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
    inventory_data = reader.reader_system('inventory.json')

    # Determine the next sale_id by examining existing sales
    # Normalize sales_data: support either a dict  or a plain list
    if isinstance(sales_data, dict):#isinstance checks if its a dict or something else and returns boolean true or false
        sales_list = sales_data.get('sales', [])
    else:
        sales_list = sales_data

    
    if isinstance(inventory_data, dict):
        inventory = inventory_data.get("inventory", [])
    else:
        inventory = inventory_data

    if not sales_list or not inventory:
        print('Empty Sales or Inventory data, cannot continue.')
        return

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



    
    # Purchase loop
    
    new_customer = 0

    while True:
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
            print('Invalid input.')
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
        for item in grouped[selected]:
            if item.get("item_id") == user_item_id:
                result = item
                break #breaks once the item is found to stop loop


        if not result:
            print('No item found with that ID.')
            continue

        qty = int(result['quantity_in_stock'])

        try:
            user_qty = int(input('How much do you want?: '))
        except ValueError:
            print('Invalid input.')
            continue

        if user_qty <= 0:
            print('Invalid quantity requested.')
            continue

        if user_qty > qty:
            print(f'Not enough stock. Available: {qty}')
            continue

        # Update inventory
        sold_qty = user_qty
        result['quantity_in_stock'] = str(qty - user_qty)

        price = float(result['price'])
        line_total = price * user_qty

        new_sale = {
            'sale_id': next_key,
            'date': date,
            'item_id': result['item_id'],
            'quantity_sold': sold_qty,
            'line_total': str(line_total)
        }

        sales_list.append(new_sale)

        writer.writer_system(sales_list, 'sales.json')

        
        writer.writer_system(inventory, 'inventory.json')

        print('Added sale:', new_sale)
        print('Total sale lines:', len(sales_list))

        new_customer = 1


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


