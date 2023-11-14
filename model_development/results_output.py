import docx
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB



def n_counter(df):
    """This function removes n number of empyty rows in the final dataset that contain the results of each model"""

    count = 0
    for col in df.columns[3:]:
        if '' in df[col].values:
            place_hold = col
            break
    cols_to_list = df[place_hold].to_list()
    for v in cols_to_list:
        if v == '':
            count+=1
                    
    return count



def calculate_percentage_of_recommended(actual_value, recommended_min_value):
    """
    Calculate the percentage of the actual nutritional value of the recommended minimum.

    :param actual_value: float, the actual value of the nutrient
    :param recommended_min_value: float, the recommended minimum value of the nutrient
    :return: float, percentage of the actual value over the recommended minimum
    """
    if recommended_min_value == 0:  # Prevent division by zero
        return 0
    if actual_value == 0:
        return 0
    percentage = (actual_value / recommended_min_value) * 100 
    return round(percentage, 2)  # Round to two decimal places for readability





def dataframe_to_docxTable(df, m):
    # Initialise the Word document
    doc = docx.Document()

    # Initialise the table
    t = doc.add_table(rows=1, cols=df.shape[1])

    # Add borders
    t.style = 'TableGrid'
    # Add the column headings
    for j in range(df.shape[1]):
        t.cell(0, j).text = df.columns[j]

    # Add the cost per meal row
    cost_row = t.add_row()
    cost_row.cells[0].merge(cost_row.cells[-1])  # This assumes you want to merge all cells for the cost row
    cost_row.cells[0].text = f"Optimal combination of foods for one meal costs ${round(m.objVal, 2)}"

    # Add the body of the data frame
    for i in range(df.shape[0]):
        row = t.add_row()
        for j in range(df.shape[1]):
            cell = df.iat[i, j]
            row.cells[j].text = str(cell)

            
    doc.save(f'../docx/tables/{m.ModelName[12:]}_results.docx')

    return f"{m.ModelName[12:]} Results Saved"



## All create dataframe for results


def output_to_table_no_sections(m, decison_var, menu_data, gurobi=gp):
#Defining variables
    price = menu_data['price'].tolist()
    menu_item = menu_data['item_name'].tolist()
    section_name = menu_data['menu_section'].tolist()

    calories = menu_data['Calories'].tolist()
    protein = menu_data['Protein (g)'].tolist()
    totalCarbohydratets = menu_data['Total Carbohydrates (g)'].tolist()
    dietaryFiber = menu_data['Dietary Fiber (g)'].tolist()
    totfat = menu_data['Total Fat (g)'].tolist()
    statFat = menu_data['Saturated Fat (g)'].tolist()
    transFat = menu_data['Trans Fat (g)'].tolist()
    cholesterol = menu_data['Cholesterol (mg)'].tolist()
    sodium = menu_data['Sodium (mg)'].tolist()
    sugars = menu_data['Total Sugars (g)'].tolist()

    vitamin_d = menu_data['Vitamin D (mcg)'].tolist()
    Calcium = menu_data['Calcium (mg)'].tolist()
    iron = menu_data['Iron (mg)'].tolist()
    Potassium = menu_data['Potassium (mg)'].tolist()


    menu_items = []
    servings = []
    nutrients = ["Calories", "Protein (g)", "Total Carbohydrate (g)", "Dietary Fiber (g)", "Total Fat (g)", "Saturated Fat (g)",
                 "Trans Fat (g)", "Cholesterol (mg)", "Sodium (mg)", "Sugars (g)", "Potassium (mg)", "Iron (mg)",
                   "Calcium (mg)"]
    nutrient_values = []
    RDA_per_meal = [2400//3, 56//3, 130//3, 28//3, 93//3, 26//3, 0//3, 300//3, 2300//3, 10//3, 3400//3, 8//3,1000//3] 

    # Adding items and their servings to the lists
    for var in m.getVars():
        if var.x > 0:
            menu_items.append(var.VarName)
            servings.append(round(var.X, 2))
    
     # Adding nutrient values to the nutrient_values list
    nutrient_values.append(gp.quicksum(round(calories[i]*decison_var[i].x, 2) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(protein[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(totalCarbohydratets[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(dietaryFiber[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(totfat[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(statFat[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(transFat[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(cholesterol[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(sodium[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(sugars[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(Potassium[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(iron[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(Calcium[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())

    # Creating the DataFrame
    df = pd.DataFrame({
        "Menu": menu_items + [""]*(len(nutrients)+1),
        "Servings": servings + [""]*(len(nutrients)+1),
        "Nutrient": [""]*(len(menu_items)+1) + nutrients,
        "Values": [""]*(len(menu_items)+1) + nutrient_values,
        "Recommended Minimum Per Meal (%)": [""]*(len(menu_items)+1) + RDA_per_meal
    })

    n = n_counter(df) # Value changes as needed
    df["Nutrient"] = df["Nutrient"].shift(-n)
    df["Values"] = df["Values"].shift(-n)
    df["Recommended Minimum Per Meal (%)"] = df["Recommended Minimum Per Meal (%)"].shift(-n)

    
    df = df.replace({None: ''})
    df = df.iloc[:-(n)]
    
    df['Values'] = pd.to_numeric(df['Values'], errors='coerce')
    df['Recommended Minimum Per Meal (%)'] =  [calculate_percentage_of_recommended(model, rec) for model, rec in zip(df['Values'], RDA_per_meal)]


    dataframe_to_docxTable(df,m)

    return df





def output_to_table_sections(m, decison_var, menu_data, gurobi=gp):
#Defining variables
    price = menu_data['price'].tolist()
    menu_item = menu_data['item_name'].tolist()
    section_name = menu_data['menu_section'].tolist()

    calories = menu_data['Calories'].tolist()
    protein = menu_data['Protein (g)'].tolist()
    totalCarbohydratets = menu_data['Total Carbohydrates (g)'].tolist()
    dietaryFiber = menu_data['Dietary Fiber (g)'].tolist()
    totfat = menu_data['Total Fat (g)'].tolist()
    statFat = menu_data['Saturated Fat (g)'].tolist()
    transFat = menu_data['Trans Fat (g)'].tolist()
    cholesterol = menu_data['Cholesterol (mg)'].tolist()
    sodium = menu_data['Sodium (mg)'].tolist()
    sugars = menu_data['Total Sugars (g)'].tolist()

    vitamin_d = menu_data['Vitamin D (mcg)'].tolist()
    Calcium = menu_data['Calcium (mg)'].tolist()
    iron = menu_data['Iron (mg)'].tolist()
    Potassium = menu_data['Potassium (mg)'].tolist()


    
    menu_items = []
    servings = []
    nutrients = ["Calories", "Protein (g)", "Total Carbohydrate (g)", "Dietary Fiber (g)", "Total Fat (g)", "Saturated Fat (g)",
                 "Trans Fat (g)", "Cholesterol (mg)", "Sodium (mg)", "Sugars (g)", "Potassium (mg)", "Iron (mg)",
                   "Calcium (mg)"]
    
    RDA_per_meal = [2400//3, 56//3, 130//3, 28//3, 93//3, 26//3, 0//3, 300//3, 2300//3, 10//3, 3400//3, 8//3,1000//3] 

    nutrient_values = []
    
    nutri_decison_var = []
    nutri_decison_var_value = []

    section_var = []
    section_var_value = []

# Adding items and their servings to the lists
    for var in m.getVars():
        if var.x > 0:
            if var.VarName in nutrients:
                nutri_decison_var.append(var.VarName)
                nutri_decison_var_value.append(round(var.X, 2))
            elif var.varName[6:] in section_name:
                section_var.append(var.VarName[6:])
                section_var_value.append(var.X)
            else:
                menu_items.append(var.VarName)
                servings.append(round(var.X, 2))
    
    
     # Adding nutrient values to the nutrient_values list
    nutrient_values.append(gp.quicksum(round(calories[i]*decison_var[i].x, 2) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(protein[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(totalCarbohydratets[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(dietaryFiber[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(totfat[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(statFat[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(transFat[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(cholesterol[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(sodium[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(sugars[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(Potassium[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(iron[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(Calcium[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())

    df = pd.DataFrame({
        "Menu": menu_items + nutri_decison_var+ [""]*((len(nutrients))-len(nutri_decison_var)),
        "Servings": servings + nutri_decison_var_value+ [""]*(len(nutrients)-len(nutri_decison_var_value)),
        "Section Name": section_var + [""]*(len(nutrients)),
        "Nutrient": [""]*(len(menu_items)) + nutrients,
        "Values": [""]*(len(menu_items)) + nutrient_values,
        "Recommended Minimum Per Meal (%)": [""]*(len(menu_items)) + RDA_per_meal
    })

    n = n_counter(df) # Value changes as needed
    df["Nutrient"] = df["Nutrient"].shift(-n)
    df["Values"] = df["Values"].shift(-n)
    df["Recommended Minimum Per Meal (%)"] = df["Recommended Minimum Per Meal (%)"].shift(-n)

    
    df = df.replace({None: ''})
    df = df.iloc[:-(n)]
    
    df['Values'] = pd.to_numeric(df['Values'], errors='coerce')
    df['Recommended Minimum Per Meal (%)'] =  [calculate_percentage_of_recommended(model, rec) for model, rec in zip(df['Values'], RDA_per_meal)]


    dataframe_to_docxTable(df,m)

    return df


def output_to_table_sections_cal_decision_var(m, decison_var, menu_data, gurobi=gp):
#Defining variables
    price = menu_data['price'].tolist()
    menu_item = menu_data['item_name'].tolist()
    section_name = menu_data['menu_section'].tolist()

    calories = menu_data['Calories'].tolist()
    protein = menu_data['Protein (g)'].tolist()
    totalCarbohydratets = menu_data['Total Carbohydrates (g)'].tolist()
    dietaryFiber = menu_data['Dietary Fiber (g)'].tolist()
    totfat = menu_data['Total Fat (g)'].tolist()
    statFat = menu_data['Saturated Fat (g)'].tolist()
    transFat = menu_data['Trans Fat (g)'].tolist()
    cholesterol = menu_data['Cholesterol (mg)'].tolist()
    sodium = menu_data['Sodium (mg)'].tolist()
    sugars = menu_data['Total Sugars (g)'].tolist()

    vitamin_d = menu_data['Vitamin D (mcg)'].tolist()
    Calcium = menu_data['Calcium (mg)'].tolist()
    iron = menu_data['Iron (mg)'].tolist()
    Potassium = menu_data['Potassium (mg)'].tolist()


    
    menu_items = []
    servings = []
    nutrients = ["Calories", "Protein (g)", "Total Carbohydrate (g)", "Dietary Fiber (g)", "Total Fat (g)", "Saturated Fat (g)",
                 "Trans Fat (g)", "Cholesterol (mg)", "Sodium (mg)", "Sugars (g)", "Potassium (mg)", "Iron (mg)",
                   "Calcium (mg)"]
    
    RDA_per_meal = [2400//3, 56//3, 130//3, 28//3, 93//3, 26//3, 0//3, 300//3, 2300//3, 10//3, 3400//3, 8//3,1000//3] 

    nutrient_values = []
    
    nutri_decison_var = []
    nutri_decison_var_value = []

    section_var = []
    section_var_value = []

# Adding items and their servings to the lists
    for var in m.getVars():
        if var.x > 0:
            if var.VarName in nutrients:
                nutri_decison_var.append(var.VarName)
                nutri_decison_var_value.append(round(var.X, 2))
            elif var.varName[6:] in section_name:
                section_var.append(var.VarName[6:])
                section_var_value.append(var.X)
            else:
                menu_items.append(var.VarName)
                servings.append(round(var.X, 2))
    
    
     # Adding nutrient values to the nutrient_values list
    nutrient_values.append(gp.quicksum(round(calories[i]*decison_var[i].x, 2) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(protein[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(totalCarbohydratets[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(dietaryFiber[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(totfat[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(statFat[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(transFat[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(cholesterol[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(sodium[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(sugars[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(Potassium[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(iron[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())
    nutrient_values.append(gp.quicksum(round(Calcium[i]*decison_var[i].x) for i in range(len(menu_data))).getValue())

    df = pd.DataFrame({
        "Menu": menu_items + nutri_decison_var+ [""]*((len(nutrients))-len(nutri_decison_var)),
        "Servings": servings + nutri_decison_var_value+ [""]*(len(nutrients)-len(nutri_decison_var_value)),
        "Section Name": section_var + [""]*(len(nutrients)+2),
        "Nutrient": [""]*(len(menu_items)) + nutrients,
        "Values": [""]*(len(menu_items)) + nutrient_values,
        "Recommended Minimum Per Meal (%)": [""]*(len(menu_items)) + RDA_per_meal
    })

    n = n_counter(df) # Value changes as needed
    df["Nutrient"] = df["Nutrient"].shift(-n)
    df["Values"] = df["Values"].shift(-n)
    df["Recommended Minimum Per Meal (%)"] = df["Recommended Minimum Per Meal (%)"].shift(-n)

    
    df = df.replace({None: ''})
    df = df.iloc[:-(n)]
    
    df['Values'] = pd.to_numeric(df['Values'], errors='coerce')
    df['Recommended Minimum Per Meal (%)'] =  [calculate_percentage_of_recommended(model, rec) for model, rec in zip(df['Values'], RDA_per_meal)]


    dataframe_to_docxTable(df,m)

    return df
    
