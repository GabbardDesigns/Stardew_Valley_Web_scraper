from bs4 import BeautifulSoup
import requests
from sdv_classes import Bundle, CommunityCenterRoom, Item
# needed for OrderedDict
from collections import OrderedDict
# needed to clear screen
import os


def scrape_web_page():
    url_bundles = "https://stardewvalleywiki.com/Bundles"
    response = requests.get(url_bundles)
    content = BeautifulSoup(response.content, "html.parser")
    return content

def get_all_rooms():
    """ Returns complete list of CommunityCenterRoom objects """
    data = scrape_web_page()
    return parse_rooms(data) 

def parse_rooms(data):
    """ returns a list of CommunityCenterRoom Objects
    Parameters: 
        data: passed from get_all_rooms, which is the website data parsed by bs
    Returns:
        rooms list: A complete list of CommunityCenterRoom Objects
    """
    room_names = data.find_all('h2')
    rooms = []
    for r_name in room_names[2:8]:       
        room_bundles = parse_room_bundles(data, r_name.text)
        rooms.append(CommunityCenterRoom(r_name.text, room_bundles))
    return rooms    

def parse_room_bundles(data, room_name):
    """ Parses beautifulsoup object to create a Bundle object if bundle is associated with room_name pased in  
    Parameters: 
        data: passed from parse_rooms(), website data parsed by bs
        room_name: passed from parse_room() for loop. 
    Returns:
        List of Bundle Objects associated with a specific community center room
    """
    bundles = []
    tables = data.find_all('table', {"class":"wikitable", "style": None})  
    for table in tables[0:30]:
        # Gets coummunity center room name associated with the bundle
        cc_room = table.find_previous_sibling('h2').text
        if room_name == cc_room:
            # Gets bundle name
            bundle_name = table.find('th').text[1:-1]
            # Gets items inside of bundle
            bundle_items = []
            if "Quality" not in bundle_name:
                rows = table.find_all('td')  
                # bundle_items = [] 
                for row in rows[2:-2:2]:
                    item_name = row.text.lstrip()
                    item_object = Item(item_name)
                    bundle_items.append(item_object)
            else:
                rows = table.find_all('td')
                # bundle_items = []
                for row in rows:
                    tbl_row = row.find_all('table')
                    for tbl in tbl_row:
                        item_name = tbl.text.lstrip() + '\n'
                        item_object = Item(item_name)
                        bundle_items.append(item_object)
                        

            # Gets number of required items to complete bundle
            required_items = 0    
            for row in rows[1].find_all(recursive=False):
                if row:
                    required_items += 1
        
            # create Bundle objects and append objects to a list
            bundle_object = Bundle(bundle_name, required_items, cc_room, bundle_items)
            bundles.append(bundle_object)

    return bundles



##### Menu Features ### 

def show_menu(choices, allow_cancellation=False):
    """
    Display a command-line menu to the user, and let them make a selection

        :param choices: A list of the options to display in the menu
        :param allow_cancellation: If the user should be able to exit the menu without making a selection (default False)
        :returns: The selection of the user, or None if cancelled.
    """
    options = {}
    # Print the options out to the user, enumerated with a numeric choice number
    for index, choice in enumerate(choices, start=1):
        print(f'{index}) {choice}')
        # We store the choice in a dictionary for easy looking-up later
        options[str(index)] = choice  
    
    # Add a cancellation option if it was requested (default is False)
    if allow_cancellation:
        print('0) Cancel')
        options['0'] = None  # If the user does choose to cancel, we will return None
    
    # Simply loop until the user makes a valid selection
    user_input = input('Select an option: ')
    while user_input not in options.keys():
        print('Invalid selection')
        user_input = input('Select an option: ')
    
    # Look up the selected item and return it
    return options[user_input]

def clear():
    """ clears the console """
    os.system('cls' if os.name =='nt' else 'clear')

def get_room_bundles(room_name):
    """ Returns a list of Bundle objects associated with a specific CommunityCenterRoom object
    Parameters: 
        room_name: name of CommunityCenterRoom Object
    Returns:
        room_bundles list: a list of Bundle objects associated with the CommunityCenterRoom passed in
    """

    rooms = get_all_rooms()
    bundles = []
    for room in rooms:
        if room.name == room_name:
            bundles.append(room.bundles)
    # list comprehension to flatten bundles list  
    room_bundles = [item for sublist in bundles for item in sublist]
    return room_bundles
    
def get_bundle_items(room_name, bundle_name):
    """ Returns a list of Item objects associated with a specific Bundle object
    Parameters: 
        room_name: name of CommunityCenterRoom Object
        bundle_name: name of Bundle object inside of the CommunityCenterRoom Object
    Returns:
        bundle_items list: a list of Item objects associated with the Bundle object passed in
    """
    
    bundles = get_room_bundles(room_name)
    items = []
    for bundle in bundles:
        if bundle.name == bundle_name:
            items.append(bundle.items)
    bundle_items = [item for sublist in items for item in sublist]
    return bundle_items

def get_names(obj_list):
    """ Retruns list of names
    Parameters: 
        obj_list: list of objects where there objects have 'name' as an attribute
    Returns:
        names list: list of the name attributes in the obj_list
    """
    names = []
    for obj in obj_list:
        names.append(obj.name)
    return names
        

def room_menu():
    """ Show the main menu """
    
    clear()
    print("Welcome to the Stardew Valley Community Center Bundle Tracker!")
    print('*' * 40)
    print("Please select a room")
    user_selected_room = show_menu(get_names(get_all_rooms()), allow_cancellation=True)
    bundle_menu(user_selected_room)

    #TODO : if 0 selected, exit out of program

def bundle_menu(room):
    """ Show menu of bundles in a specific room """

    clear()
    print("Please select a bundle")
    user_selected_bundle = show_menu(get_names(get_room_bundles(room)), allow_cancellation=True)
    item_menu(room, user_selected_bundle)

    #TODO : add conditional to check for Vault. If Vault selected, selcting the bundle should mark the bundle as 'complete'
    #TODO : if 0 selected go back to room_menu


def item_menu(room, bundle):
    """ Show menu of items in a specific bundle """

    clear()
    print("Select the item you've donated to the Community Center")
    user_selected_item = show_menu(get_names(get_bundle_items(room, bundle)), allow_cancellation=True)

    #TODO : user_selected_item should switch the item.donated value. If that value is False, switch to true. If true, switch to false
    #TODO : while user_selected_item is not 0, let user continue to select items.
    #TODO : if 0 selected, go back to bundle_menu

room_menu()


# items = get_bundle_items("Crafts Room", "Fall Foraging Bundle")
# for item in items:
#     print(item.item_id)

# bundles = get_room_bundles('Crafts Room')
# for bundle in bundles:
#     print(bundle.items)

# rooms = get_all_rooms()
# for room in rooms:
#     print(room)

