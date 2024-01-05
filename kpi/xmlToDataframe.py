from genericpath import exists
from importlib.resources import path
import pandas as pd
from lxml import etree
import glob
import pathlib
# def iter_xml(root, key_attr, initial_list):
#     result_list = initial_list
#     for item in root.iter(key_attr):
#         result_list.append(item.text)
#     return result_list

def xmltoCSV(input_file,output_file):
    tree = etree.parse(input_file) #create an ElementTree object 
    start_time = tree.xpath('.//mts')[0].text
    end_time= tree.xpath('.//ts')[0].text
    headers = tree.xpath('.//mt')
    header_list = ['Start_time', 'End_time','NE', 'Object']
    for header in headers:
        header_list.append(header.text)
    mv_data = tree.xpath('.//mv')
    value_list = []
    for mv in mv_data:
        mv_list = [start_time,end_time]
        objectItem = mv.find('moid').text.split('/')
        mv_list.append(objectItem[0])
        mv_list.append(objectItem[1])
        r_data = mv.findall('.//r')
        for r in r_data:
            mv_list.append(r.text)
        value_list.append(mv_list)
    df = pd.DataFrame(value_list,columns=header_list)
    print(df)
    output_file = pathlib.Path(output_file)
    df.to_csv(output_file, mode ='a', index=False, header=not output_file.exists())

# Find all the files with specific prefix and store to list
files = glob.glob('kpi/tmpMeasFiles/HOST02_pmresult_1693700401_5*')
print(files)
for input_file in files:
    output_file = r'kpi/output/HOST02_pmresult_1693700401_5.csv'
    xmltoCSV(input_file,output_file)