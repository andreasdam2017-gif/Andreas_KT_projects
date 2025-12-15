import reader
import writer
import binary_search

def add_item_inventory():
    #The function adds a new item to the inventory.
    #Returns : The inventory

    #Loads the inventory json file
    inventory_dict = reader.reader_system('inventory.json')
    
    #Asks the user for the inputs
    item_id = str(int(inventory_dict["inventory"][-1]["item_id"]) + 1)
    item_name = input('Input the item name : ')
    category = input('Input the item category : ')
    price = input('Input the item price : ')
    quantity_in_stock = input('Input the quantity in stock of the item : ')

    inventory_dict['inventory'].append({'item_id' : item_id,
                                        'item_name' : item_name,
                                        'category' : category,
                                        'price' : price,
                                        'quantity_in_stock' : quantity_in_stock})
    
    writer.writer_system(inventory_dict, 'inventory.json')

def delete_item_inventory():
    #The function deletes a item from the inventory.
    #Returns : The inventory

    #Loads the inventory json file
    inventory_dict = reader.reader_system('inventory.json')
    removed = 0
    removable_input = input('Input the item id you want to remove : ')
    # Searches over the dictionary of lists and checks if the item exists in the inventory. Then deletes it.
    removable_index = binary_search.BS(int(removable_input), inventory_dict['inventory'])
    if removable_index >= 0:
        inventory_dict['inventory'].pop(removable_index)
    else:
        print('Item does not exist')

    writer.writer_system(inventory_dict, 'inventory.json')

    #print(inventory_dict)


def update_inventory():
    #The function updates an item and displays it for the user
    #Arguments : none
    #Returns : none

    #initialize variables
    inventory_dict = reader.reader_system('inventory.json')
    update_input = input('Input the item id you want to update : ')
    print('_'*100, '\n')
    item_inventory = 0
    #Searching for the item id
    for index, (keys, category) in enumerate(inventory_dict.items()):               #Pointer pointing to the category list
        for item in category:
            if item['item_id'] == update_input:                                     #If the item exists then we update it
                index_keys = list(enumerate(item.keys()))
                item_inventory = 1
                #Prints the options menue for the item to be updated
                for i, key in index_keys:
                    if key != 'item_id':
                        print(f'{i} : {key:<17} : {item[key]}')
                print('0 : BACK\n')

                options_input = input('Input the index you want to update : ')

                #Loop that allows you to update multiple items and back out
                while options_input != '0':
                    custom_input= input('What do you want to change the value to? : ')
                    item[index_keys[int(options_input)][1]] = custom_input

                    print()
                    for i, key in index_keys:
                        if key != 'item_id':
                            print(f'{i} : {key:<17} : {item[key]}')
                    print('0 : BACK\n')
                    options_input = input('Input the index you want to update : ')

                #print(item)
                writer.writer_system(inventory_dict, 'inventory.json')
                break
    
    if item_inventory == 0:
        print('Item does not exist, consider adding it to the inventory instead.')

if __name__ == '__main__':
    #add_item_inventory()
    delete_item_inventory()
    #update_inventory()
