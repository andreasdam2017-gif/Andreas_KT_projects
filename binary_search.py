



def BS(search_id, list_dict):
    # Binary search algorithm
    # Arguments are the id you search for and a list of dicts with the key "item_id" in it
    # Returns the index for the value you are searching for or -1 if it does not exist
    try:
        left = 0
        right = len(list_dict) - 1

        while left <= right:
            mid = (left + right) // 2

            if int(list_dict[mid]['item_id']) == search_id:
                return mid

            if int(list_dict[mid]['item_id']) < search_id:
                left = mid + 1
            else:
                right = mid - 1

        return -1
    except ValueError:
        print('An item_id is not an integer. Please regenerate the inventory from a valid backup.')
