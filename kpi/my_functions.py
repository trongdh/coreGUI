from genericpath import isfile
import gzip
import shutil
import pandas as pd
from lxml import etree
import glob
import pathlib
import os
import paramiko
import fnmatch

# Function to unzip file


def gunzip_shutil(source_filepath, dest_filepath, block_size=65536):
    with gzip.open(source_filepath, 'rb') as s_file, \
            open(dest_filepath, 'wb') as d_file:
        shutil.copyfileobj(s_file, d_file, block_size)

# Function to convert xml to excel


def xmltoExel(input_file, output_file):
    # Fetch data from xml file to dataframe
    tree = etree.parse(input_file)  # create an ElementTree object
    start_time = tree.xpath('.//mts')[0].text
    end_time = tree.xpath('.//ts')[0].text
    headers = tree.xpath('.//mt')
    # Initial some column names
    header_list = ['Start_time', 'End_time', 'NE', 'Object']
    for header in headers:
        header_list.append(header.text)
    mv_data = tree.xpath('.//mv')
    value_list = []
    for mv in mv_data:
        mv_list = [start_time, end_time]
        objectItem = mv.find('moid').text.split('/')
        mv_list.append(objectItem[0])
        mv_list.append(objectItem[1])
        r_data = mv.findall('.//r')
        for r in r_data:
            mv_list.append(r.text)
        value_list.append(mv_list)
    new_df = pd.DataFrame(value_list, columns=header_list)
    new_df['Start_time'] = pd.to_datetime(
        new_df['Start_time'], format="%Y%m%d%H%M")
    new_df['End_time'] = pd.to_datetime(
        new_df['End_time'], format="%Y%m%d%H%M")

    # Check if excel file exists
    if os.path.isfile(output_file):
        old_df = pd.read_excel(output_file, engine='openpyxl')
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
        combined_df.to_excel(output_file, index=False, sheet_name='Sheet1')
    else:
        new_df.to_excel(output_file, engine='openpyxl', index=False)

# Function to convert xml to CSV


from lxml import etree
import pandas as pd
import pathlib

def xml_to_csv(input_file, output_file):
    tree = etree.parse(input_file)
    start_time = tree.find('.//mts').text
    end_time = tree.find('.//ts').text

    headers = [header.text for header in tree.findall('.//mt')]
    header_list = ['Start_time', 'End_time', 'NE', 'Object'] + headers

    value_list = []
    for mv in tree.findall('.//mv'):
        mv_list = [start_time, end_time]
        object_item = mv.find('moid').text.split('/')
        mv_list.extend(object_item)
        r_data = [r.text for r in mv.findall('.//r')]
        mv_list.extend(r_data)
        value_list.append(mv_list)

    df = pd.DataFrame(value_list, columns=header_list)
    output_file = pathlib.Path(output_file)
    df.to_csv(output_file, mode='a', index=False, header=not output_file.exists())


# Function to sftp file


def sftp_to_get_latest_file(host, port, username, password, local_path, remote_path, template_name, meas_period):
    latest_time = 0
    latest_file = None

    try:
        transport = paramiko.Transport((host, port))
        transport.connect(None, username, password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print('Connected to SFTP successfully')

        for file_attr in sftp.listdir_attr(remote_path):
            if (template_name in file_attr.filename) and (('_' + meas_period + '_') in file_attr.filename) and file_attr.st_mtime > latest_time:
                latest_time = file_attr.st_mtime
                latest_file = file_attr.filename

        if latest_file is not None:
            remote_file_path = os.path.join(remote_path, latest_file)
            local_file_path = os.path.join(local_path, latest_file)

            sftp.get(remote_file_path, local_file_path)
            
            # Decompress if the file is gzipped
            if latest_file.endswith('.gz'):
                with gzip.open(local_file_path, 'rb') as f_in, open(local_file_path.replace('.gz', ''), 'wb') as f_out:
                    f_out.write(f_in.read())

                os.remove(local_file_path)  # Remove the gzipped file

        # Close SFTP
        sftp.close()
        transport.close()

    except Exception as e:
        print(f"An error occurred: {e}")
