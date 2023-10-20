# Taco Bell Menu Optimization (LP)

## Description 
As a college student, eating health is complex. We know what's essential for our bodies, but with commitments like attending class, completing assignments on time, exams, papers, parties, discussion posts, and, for some, balancing athletics, time is hard to find, and on top of that, the money need to prep meals with high-quality ingredients is expensive. Thankfully, we students only have to experience this briefly (I hope). But what about those who need the appropriate knowledge about what they should eat or more time or money to cook/purchase high-quality meals?

For many fast food restaurants, it is an option that can fulfill their dietary needs while knowing that this route is less beneficial than eating whole food ingredients. This project aims to create an optimal meal using Taco Bell Menu items using integer linear programming and various models that minimize costs or maximize nutritional benefits, factoring in nutrients and financial constraints. The nutritional constraints are based on the Dietary Guidelines for Americans, 2020-2025, specifically table A1-2: https://www.dietaryguidelines.gov/sites/default/files/2020-12/Dietary_Guidelines_for_Americans_2020-2025.pdf.

After completing each model, we will compare each to see what objective function and constraints produce the best outcome.


## Author and Contact Info.
- Name: Noor Ashrifeh
- Email: nashrifeh@outlook.com
- Phone number: (203)-820-0488

## Programming Language and Libaries
- Python and Jupiter Notebook
- Version 3.11.4
- Libaries: Pandas, Numpy, Selenium, Gurobi, Plotly

## Data
- The primary dataset will come from the official Taco Bell website, only using the sites that allow web crawlers; this information can be viewed here: https://www.tacobell.com/robots.txt. Using Selenium to automate the web scraping process, I pulled information such as item names, macro/micronutrients, allergens, and indigents. All code files can be found under the data processing file.