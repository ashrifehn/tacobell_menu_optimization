import docx
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB


def n_counter(df):
    """This function removes n number of empyty rows in the final dataset that contain the results of each model"""
    count = 0

    for col in df.columns[2:]:
        if '' in df[col].values:
            list = df[col].to_list()

            for v in list:
                if v == '':
                    count+=1
                    
    return count


def dataframe_to_docxTable(df, m):
    """Creates a table in Word, allows me to copy and paste the results directly into my final paper instead of manually creating it
    """
    # Initialise the Word document
    doc = docx.Document()

    # Initialise the table
    t = doc.add_table(rows=1, cols=df.shape[1])
    
    # Add borders
    t.style = 'TableGrid'
    # Add the column headings
    for j in range(df.shape[1]):
        t.cell(0, j).text = df.columns[j]
    # Add the body of the data frame
    for i in range(df.shape[0]):
        row = t.add_row()
        for j in range(df.shape[1]):
            cell = df.iat[i, j]
            row.cells[j].text = str(cell)
            
    doc.save(f'../docx/tables/{m.ModelName[12:]}_results.docx')

    return "EOM1 Results Saved"





# Function
def output_to_table(m, decison_var, menu_data, gurobi=gp):
    """Creates a pandas dataframe to display the results"""
    #Defining variables
    price = menu_data['price'].tolist()
    menu_item = menu_data['item_name'].tolist()
    section_name = menu_data['menu_section'].to_list()

    calories = menu_data['Calories'].tolist()
    protein = menu_data['Protein (g)'].tolist()
    totalCarbohydratets = menu_data['Total Carbohydrates (g)'].tolist()
    dietaryFiber = menu_data['Dietary Fiber (g)'].tolist()
    totfat = menu_data['Total Fat (g)'].tolist()
    statFat = menu_data['Saturated Fat (g)'].to_list()
    transFat = menu_data['Trans Fat (g)'].to_list()
    cholesterol = menu_data['Cholesterol (mg)'].tolist()
    sodium = menu_data['Sodium (mg)'].tolist()
    sugars = menu_data['Total Sugars (g)'].tolist()

    vitamin_d = menu_data['Vitamin D (mcg)'].to_list()
    Calcium = menu_data['Calcium (mg)'].to_list()
    iron = menu_data['Iron (mg)'].to_list()
    Potassium = menu_data['Potassium (mg)'].to_list()

    menu_items = []
    servings = []
    nutrients = ["Calories", "Protein (g)", "Total Carbohydrate (g)", "Dietary Fiber (g)", "Total Fat (g)", "Saturated Fat (g)",
                 "Trans Fat (g)", "Cholesterol (mg)", "Sodium (mg)", "Sugars (g)", "Potassium (mg)", "Iron (mg)",
                   "Calcium (mg)", "Vitamin D (mcg)"]
    nutrient_values = []
    
    # Adding items and their servings to the lists
    for var in m.getVars():
        if var.x > 0:
            menu_items.append(var.VarName)
            servings.append(round(var.X, 2))
    
    # Adding nutrient values to the nutrient_values list
    nutrient_values.append(gp.quicksum(calories[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(protein[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(totalCarbohydratets[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(dietaryFiber[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(totfat[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(statFat[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(transFat[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(cholesterol[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(sodium[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(sugars[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(Potassium[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(iron[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(Calcium[i]*decison_var[i].x for i in range(len(menu_data))))
    nutrient_values.append(gp.quicksum(vitamin_d[i]*decison_var[i].x for i in range(len(menu_data))))


    # Creating the DataFrame
    df = pd.DataFrame({
        "Menu": ["Cost per Meal"] + menu_items + [""]*len(nutrients),
        "Servings": ["$"+str(round(m.objVal, 2))] + servings + [""]*len(nutrients),
        "Nutrient": [""]*(len(menu_items)+1) + nutrients,
        "Values": [""]*(len(menu_items)+1) + nutrient_values
    })

    n = n_counter(df)  # Value changes as needed
    df["Nutrient"] = df["Nutrient"].shift(-n)
    df["Values"] = df["Values"].shift(-n)
    
    df = df.replace({None: ''})
    df = df.iloc[:-(n-1)]
    
    
    dataframe_to_docxTable(df,m)


    return df