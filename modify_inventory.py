import reader


def add_item_inventory():
    #The function adds a new item to the inventory.
    # Returns : The inventory

    # Loads the inventory json file
    inventory_dict = reader.reader_system('inventory.json')

    # Asks the user for the inputs
    item_id = input('Input the item id : ')
    item_name = input('Input the item name : ')
    category = input('Input the item category : ')
    price = input('Input the item price : ')
    quantity_in_stock = input('Input the quantity in stock of the item : ')

    inventory_dict[category].append({'item_id' : item_id,
                                        'item_name' : item_name,
                                        'category' : category,
                                        'price' : price,
                                        'quantity_in_stock' : quantity_in_stock})
    
    return inventory_dict

def delete_item_inventory():
    #The function deletes a item from the inventory.
    # Returns : The inventory

    # Loads the inventory json file
    inventory_dict = reader.reader_system('inventory.json')
    removed = 0
    removable_input = input('Input the item id you want to remove : ')
    for index, (key, category) in enumerate(inventory_dict.items()):            #Pointer pointing to the category list
        for item in category:
            if item['item_id'] == removable_input:
                category.remove(item)
                removed = 1
    
    if removed == 0:
        print('Item does not exist')

    print(inventory_dict)
    return inventory_dict

print(delete_item_inventory())
