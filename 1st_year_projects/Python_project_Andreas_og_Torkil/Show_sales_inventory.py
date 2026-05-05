
import reader_writer

def display():
    """
    This Function shows files in inventory or in Sales, by first checking what file you wanna use.
    Then, it takes its indexes and list each key value pair with its index number in a nice readable way.
    
    It does not return any values, just displays information.
    """
   
    print('You can only display "sales.json" and "inventory.json"')
    display_file = input('Which file do you want to display : ')
    if display_file == 'sales.json' or display_file == 'inventory.json':
        display_items = reader_writer.reader_system(display_file)
        if not display_items:
            print('No  data available to display, please regenerate the dictionary.')
            input('Going back to main menu, press enter to confirm')
            return
        for file_storage, items in display_items.items():#We take the outer dict and display its name in a for loop
            print()
            print('-' * 40)
            print(f'File Storage: {file_storage}')     
            for index, item in enumerate(items, start=1):
                print(f'  Item {index}:')                
                for key, value in item.items():          #We print the key and values in the index
                    print(f'    {key} = {value}')
    else:
            print('Error, you typed the wrong file name')
    
    input('Going back to main menu, press enter to confirm')
    
                       
if __name__ == "__main__":  
    display()#Change name if you wish to see inventory.json or sales.json file

    

   
    