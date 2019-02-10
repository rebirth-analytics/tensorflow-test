import re
import os
import mysql.connector
from mysql.connector import errorcode

UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
try:
    conn = mysql.connector.connect(
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        host=os.environ['DB_HOST'],
        port=3306,
        database=os.environ['DB_SCHEMA'], 
        ssl_ca=os.environ['CERT_FILE'],
        ssl_verify_cert=True)
    print("Connection established")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with the user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cursor = conn.cursor(dictionary=True)

def is_uuid(uuid):
    return UUID_PATTERN.match(uuid)

def locate_report_data(uuid):
    cursor.execute("SELECT * FROM reports WHERE uuid = UuidToBin('{0}') ;".format(uuid))
    row = cursor.fetchone()
    return row

