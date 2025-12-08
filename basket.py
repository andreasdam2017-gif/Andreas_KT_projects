import json
import os
import reader
import writer
from datetime import datetime, timedelta

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
     
    if  sales_list == {} or inventory_categories == {}:
        print('Empty Sales or Inventory Dictionary, cannot continue.')
        return


        
    # We'll compute next_key when a sale starts (so each sale gets a fresh id or continue having the old one)

    # Outer loop: allow starting multiple sales until the user exits
    
    while True:
        try:
            ask = int(input('Would you like to purchase something? Press 1 to buy and anything else to cancel: '))
                    
        except ValueError:#Incase user writes a non interger
            print('Invalid input — cancelling.')
            break

        if ask != 1:
            print('Purchase cancelled.')
            break
        
        verify = int(input('Are you a new customer or do you wish to buy more as the same customer? Press 1 if new or Press 2 to continue shopping'))
        
        # Initialize next_key based on customer type
        next_key = None
        if verify == 1:
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
        
        
        # Determine the date for this sale: increment last sale's date by 1 day if possible,
        # otherwise use today's date. Expected stored date format is YYYY-MM-DD.
        if sales_list:
            last_date_str = sales_list[-1].get('date', '')
            try:
                last_date = datetime.strptime(last_date_str, "%Y-%m-%d") #strptime makes string into datetime object
                date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d") # timedelta adds one day
            except Exception:
                date = datetime.now().strftime("%Y-%m-%d") #If error occurs we use todays date
        else:
            date = datetime.now().strftime("%Y-%m-%d")#If no sales exist, use today's date
        
        # Show available categories
        for category in inventory_categories.keys():
            print(f"  {category}")
        user_cat = input('What Category? (type Dairy to get Dairy products)').strip()

        if user_cat in inventory_categories:
            items = inventory_categories[user_cat]
            print(f'\nItems in {user_cat}:')
            for item in items:
                print(f'  ID: {item['item_id']} - Name: {item['item_name']} - Qty: {item['quantity_in_stock']}')

            user_item_id = input('What Item ID do you want? ').strip()
            # Create mapping item_id
            item_dict = {item['item_id']: item for item in items}
            result = item_dict.get(user_item_id)

            if result:
                print(f'You selected: {result}')

                qty = int(result['quantity_in_stock'])
                user_qty = int(input('How many do you want? '))
                if user_qty <= 0 or user_qty != int(user_qty): #Makes sure user cant buy negative or non interger amounts
                    print('Invalid quantity requested.')
                    continue

                if user_qty <= qty:  # Check stock before allowing the sale
                    sold_qty = user_qty
                    new_qty = qty - user_qty
                    result['quantity_in_stock'] = str(new_qty)
                    

                    print(f'Remaining quantity: {new_qty}')


                    # Build a lookup dict keyed by sale_id for quick access
                    



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

                    print("Added sale:", new_sale)
                    # show total number of sale lines 
                    print('Total number of sale lines now:', len(sales_list))

                    writer.writer_system(inventory_categories, 'inventory.json')  # updates inventory after sale been concluded
                else:
                    print(f'Not enough stock. Available: {qty}, Requested: {user_qty}')
            else:
                print(f'No item found with ID {user_item_id}')
        else:
            print(f'Category {user_cat} not found')


process_sale()