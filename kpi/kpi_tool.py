from datetime import datetime
from cryptography.fernet import Fernet
from pytz import timezone
import os
from my_functions import *

# Initial variables
passwordKey = 'KCgkMbOobhNHTd0orBrvZqc-0v2VgN3sPJdxvEmJh4I='
fernet = Fernet(passwordKey)
encPassword = 'gAAAAABlio3IGMym6wK574-qWG4w9K7bnYDKINmNDtadWllTne9kP1XnbWeokaJreb_EgNV7iZ_FwNy_l103YMQvek_YtfTaDw=='


# Initial temporary folder to store XML file
currentPath = os.getcwd()
tmpLocalMeasPath = currentPath + "/kpi/tmpMeasFiles/"
tmpLocalMeasPath = tmpLocalMeasPath.replace(os.sep, '/')

# Initial subset_id and period, can modify to load from csv file.
# tempalteName = 'KPI_HSS_EPS'
# tempalteName = 'KPI_Sub_HLR_HSS'
tempalteName = 'KPI_HLR_MAP'
measPeriod = '5'

# Get date-time
format = "%Y%m%d"
nowHaiti = datetime.now(timezone('America/Port-au-Prince')).strftime(format)

# This is folder in OSS
measFilePath = "/opt/oss/server/var/fileint/pm/pmexport_" + nowHaiti + "/"

# Open a transport
host, port = "10.228.36.134", 22

# Auth
username = "sopuser"
password = fernet.decrypt(encPassword).decode()


# SFTP to get latest file with file prefix

sftpToGetLatestFile(host, port, username, password,
                    tmpLocalMeasPath, measFilePath, tempalteName, measPeriod)

# Convert xml to CSV

input_file_prefix = 'kpi/tmpMeasFiles/*' + tempalteName + '*'
output_file = 'kpi/output/' + tempalteName + '_' + measPeriod + '.csv'

# File all the file with prefix in specific folder and store to List
files = glob.glob(input_file_prefix)
for input_file in files:
    xmltoCSV(input_file, output_file)

# Convert xml to Excel

input_file_prefix = 'kpi/tmpMeasFiles/*' + tempalteName + '*'
output_file = 'kpi/output/' + tempalteName + '_' + measPeriod + '.xlsx'

# File all the file with prefix in specific folder and store to List
files = glob.glob(input_file_prefix)
for input_file in files:
    xmltoExel(input_file, output_file)
