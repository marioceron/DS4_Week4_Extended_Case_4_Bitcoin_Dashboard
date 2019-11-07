import os
from os import environ

my_db      = os.environ.get('DB_NAME')
my_user    = os.environ.get('DB_USER')
my_passwd  = os.environ.get('DB_USER_PASSWORD')
my_db_port = os.environ.get('DB_PORT')
my_host_endpoint =  os.environ.get('DB_ENDPOINT_HOST')

print('my_db=')
print(os.environ.get('DB_NAME'))
#print(os.environ["DB_NAME"])
print('end')
#sql_conn_str='postgresql://'+my_user+':'+my_passwd+'@'+my_rds_host_endpoint+':'+my_db_port+'/'+my_db

