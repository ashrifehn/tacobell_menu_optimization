# Developled on Python version 3.11.4

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from datetime import date

from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

today=date.today()

# Function that parses through the nutritonal data, and returns a dictionary 

def nutrition_info_parsing(text):
    nutrition_lines = [line.strip() for line in text.split("\n") if line.strip()]

    nutrient_dict = {}

    i = 0
    while i < len(nutrition_lines):
        line = nutrition_lines[i]

        if line == 'Calories':
            nutrient_dict['Calories'] = float(nutrition_lines[i+1])
            i += 2  # Increment by 2 to jump to the next component

        elif any(word in line for word in ['Fat' ,'Cholesterol','Includes', 'Sugars', 'Sodium', 'Carbohydrates', 'Fiber', 'Protein', 'Vitamin D', 'Calcium', 'Iron', 'Potassium']):
            nutrient = line.split()
            
            # Check if the next line contains a value (like '8g', '25mg', etc.)
            if i+1 < len(nutrition_lines) and any(val in nutrition_lines[i+1] for val in ['g', 'mg', 'mcg']):

                # Use the nutrient as key and the next line as value
                nutrient_name = ' '.join(nutrient[:-1])  # Exclude the value (like '8g') from the nutrient name
                unit = ''.join([char for char in nutrient[-1] if not char.isdigit() and char != '.'])
                nutrient_key = f"{nutrient_name} ({unit})"
                nutrient_value = float(''.join([char for char in nutrient[-1] if char.isdigit() or char == '.']))

                if '<' in nutrient_name:
                    nutrient_name = nutrient_name.replace('<', '').strip()
                    nutrient_key = f"{nutrient_name} ({unit})"

                nutrient_dict[nutrient_key] = nutrient_value
                
                i += 2  # Increment by 2 to jump to the next component

            else:
                i += 1  # No expected value on the next line, move on

        else:
            i += 1


    return nutrient_dict





def get_menu_section_links(driver, base_url="https://www.tacobell.com", menu_endpoint="/food", store_location = "?store=038911#"):
    driver.get(base_url+menu_endpoint)


    cites_allowed_WS = [
    "/food/tacos", 
    "/food/burritos",
    "/food/quesadillas",
    "/food/nachos",
    "/food/sides-sweets",
    "/food/drinks",
    "/food/power-menu",
    "/food/vegetarian",
    "/food/breakfast",
    "/food/specialties"]



    # Look into https://www.tacobell.com/sitemap.xml a little bit more.

    # sleep(5)  # Wait 5 seconds before searching for the element

    # Using XPath to locate the main parent div that contains all the links
    element = driver.find_element(By.XPATH, '//div[contains(@class, "styles_menu-grid__9lRvR")]')


    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')

    # Extract all the links and their href values
    links = [a['href'] for a in soup.find_all('a') if a.has_attr('href')]

    allowed_links = [link for link in links if link.split("?")[0] in cites_allowed_WS]
    
    section_links = [base_url + link + store_location for link in allowed_links]


    return section_links




def pulling_data(driver, store_location="?store=038911#", base_url="https://www.tacobell.com"):
    menu_section_links = get_menu_section_links(driver)

    menu_data = []
    for f in menu_section_links:
        driver.get(f)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        heading = soup.find('h1')
        
        links = [a['href'] for a in soup.find_all('a', class_='styles_product-title__6KCyw')]
        
        full_links = [base_url + link + store_location+"#" if not link.endswith('1') else base_url+link+"#" for link in links]

        for item in full_links:
            driver.get(item)

            subpage_soup = BeautifulSoup(driver.page_source, 'html.parser')
            header = subpage_soup.find_all('h1')
            item_name = [i.text for i in header if len(i.text) !=0]

            price = subpage_soup.find('span', class_='styles_price__3-xtw')
            # print(f"Menu Section: {heading.text}, Item name: {item_name[0]}, Price: {price.text}")


            try:
                # Check if the "Nutrition Info" link exists on the webpage
                nutrition_link = driver.find_element(By.LINK_TEXT, "Nutrition Info")
                nutrition_link.click()
                sleep(2)
                
                driver.switch_to.frame(driver.find_element(By.XPATH, '//iframe[contains(@src, "nutritionix.com/label/popup/item/")]'))

                
                # Grabbing nutri info
                nutrition_info = driver.find_element(By.CLASS_NAME, 'nf')
                nutrition_info_txt = nutrition_info.text

                # print(f"Nutrition info for {item_name[0]} grabbed")





                # Grabbing allergen info; still need to find a way to clean this text
                # allergen_info = driver.find_element(By.CLASS_NAME, "allergenInfo")
                # allergen_info_text = allergen_info.text

            

                # Append the data to the taco_data list
                menu_data.append({
                    'item_name': item_name[0],
                    'price': float(price.text[1:]),
                    'menu_section': heading.text,
                    **nutrition_info_parsing(nutrition_info_txt)
                })

                print(f"All of the {item_name[0]} data added to the master dataset")



                
            except NoSuchElementException:  # Element not found
                continue  # Go to the next item in the loop

        print(f"\nThe {heading.text} section has been sucessfully pulled")


    print("\nAll individual items from Taco Bell's menu have been acquired")


    return menu_data







def clean_taco_bell_menu(input_csv_path, output_csv_path=None):
    # Step 1: Set options
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    
    # Step 2: Read the data
    menu_data_df = pd.read_csv(input_csv_path, index_col=0)
    
    # Step 3: Fill missing values and adjust columns
    menu_data_df.fillna(0, inplace=True)
    menu_data_df['Total Sugars (g)'] = menu_data_df['Sugars (g)'] + menu_data_df['Includes (g)']
    menu_data_df.drop(columns=['Sugars (g)', 'Includes (g)'], inplace=True)
    
    # Step 4: Filter rows based on price
    menu_data_df = menu_data_df[menu_data_df['price'] >= 1.00]
    
    # Step 5: Drop discontinued or limited-time items
    discontinued_items = [
        'Steak and Bacon Grilled Cheese Burrito',
        'Strawberry Twists',
        'Wild Strawberry Creme Delight Freeze',
        'Blue Raspberry Freeze',
        'Breakfast Taco Sausage',
        'Breakfast Taco Bacon',
        'Breakfast Taco Potato',
        'Double Berry Freeze',
        'Bell Breakfast Box'
    ]
    menu_data_df = menu_data_df[~menu_data_df['item_name'].isin(discontinued_items)]
    
    # Step 6: Check and remove duplicates
    menu_data_df = menu_data_df.drop_duplicates(subset=['item_name'], keep="last")
    
    # Step 7: Save cleaned data
    if output_csv_path is None:
        today = date.today()
        output_csv_path = f"../data/cleaned_taco_bell_menu_items_{today}.csv"
    menu_data_df.to_csv(output_csv_path)
    
    return menu_data_df


