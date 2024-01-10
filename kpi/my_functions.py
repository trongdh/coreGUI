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


def sftpToGetLatestFile(host, port, username, password, locaPath, remotePath, tempalteName, measPeriod):
    latest = 0
    latestfile = None
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(None, username, password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print('Connect sftp ok')
        # Get all files with prefix
        # measFilePrefix = 'HOST02_pmresult_1693700401_5'
        # for fileattr in sftp.listdir_attr(measFilePath):
        #     if fileattr.filename.startswith(measFilePrefix):
        #         latestfile = fileattr.filename
        #         print(latestfile)
        #         sftp.get(measFilePath + "/" + latestfile, tmpMeasFolder + latestfile)
        #         gunzip_shutil(tmpMeasFolder + latestfile, tmpMeasFolder + latestfile.replace('gz',''))

        # Get latest file with prefix, can modify to load the measFilePrefix

        for fileattr in sftp.listdir_attr(remotePath):
            # if fileattr.filename.startswith(measFilePrefix) and fileattr.st_mtime > latest:
            if (tempalteName in fileattr.filename) and (('_' + measPeriod + '_') in fileattr.filename) and fileattr.st_mtime > latest:
                latest = fileattr.st_mtime
                latestfile = fileattr.filename
        if latestfile is not None:
            sftp.get(remotePath + "/" + latestfile, locaPath + latestfile)
            gunzip_shutil(locaPath + latestfile, locaPath +
                          latestfile.replace('gz', ''))
            if os.path.exists(locaPath + latestfile):
                os.remove(locaPath + latestfile)
            else:
                print('File does not exist')
        # Close SFTP
        sftp.close()
        transport.close()
    except Exception as e:
        print(f"Something wrong: {e}")
