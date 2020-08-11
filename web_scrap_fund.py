# a simple script used for webscrapping chosen funds data from a website for a 
# specific day and save/append it to a json file

# script can be set up in windows scheduler to run everyday automatically

from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

# website for scrapping
url = "https://www.bankier.pl/fundusze/notowania/wszystkie"

# getting the entire website as lxml
html_content = requests.get(url)
# change encoding to process polish signs
html_content.encoding = 'utf-8'
# get text
content = html_content.text
soup = BeautifulSoup(content, 'lxml')

# finding specific table in website
fund_table = soup.find("table", attrs = {"class": "sortTableMixedData floatingHeaderTable"})
# finding all tr in table head
fund_table_data = fund_table.thead.find_all("tr")

# getting headers for table columns
t_headers = []
for th in fund_table_data[0].find_all("th"):
    t_headers.append(th.text.replace("\n",' ').strip())

# getting values from table/ rows
table_data = []
for tr in fund_table.tbody.find_all("tr"): # each row in tbody of table is tr
    t_row = {}
    for td, th in zip(tr.find_all("td"), t_headers): # each cell in row is td
        t_row[th] = td.text.replace('\n',' ').strip()
    table_data.append(t_row)

# import list of funds avaible for me
funds_list = pd.read_csv('funds_list.csv', encoding='utf-8', index_col=0)
# convert to list
funds_list = list(funds_list['0'])
# create dictionary for funds from the list
table_dict = {}
for ii in table_data:
    for jj in funds_list:
        if jj in ii["Nazwa funduszu AD"]:
            table_dict[ii["Nazwa funduszu AD"]]={ii["Data AD"]:float(ii["Kurs AD"].replace(',','.'))}


def merge(old, new, path=None):
    # merges dictonaries
    # works for dictionaries of dictionaries
    # changes old
    
    if path is None:
        # initial path, for outermost dic is empty
        path = []
    for key in new:
        # checks if keys match
        if key in old:
            # checks if there is dictionary inside of dictionary
            if isinstance(old[key], dict) and isinstance(new[key], dict):
                # if there is then runs the function again going into that dict
                merge(old[key], new[key], path + [str(key)])
            elif old[key]==new[key]:
                pass
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            # if there is no such key in old then it creates it
            old[key]=new[key]
    return old


try:
    # open json file to dict
    with open("C:\\Users\\Pawel\\Documents\\Github\\projects\\personal_invest_dash\\data\\funds_rates.json", 'r', encoding='utf-8') as f_saved:
        funds_file = json.load(f_saved)
        # update dict
    merge(funds_file, table_dict)
    # save back to file/overwrite the existing file
    with open("C:\\Users\\Pawel\\Documents\\Github\\projects\\personal_invest_dash\\data\\funds_rates.json", 'w', encoding='utf-8') as f_save:
        json.dump(funds_file, f_save, ensure_ascii=False)
except:    
    # save dict to json
    with open("C:\\Users\\Pawel\\Documents\\Github\\projects\\personal_invest_dash\\data\\funds_rates.json", "w", encoding='utf-8') as f_save:
        json.dump(table_dict, f_save, ensure_ascii=False)