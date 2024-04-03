import mysql.connector
from mysql.connector import errorcode

__cnx = None
def get_connection():
    global __cnx
    if __cnx is None:
        try:
            __cnx = mysql.connector.connect(user='root', password='123456789',
                                            database='details',host='127.0.0.1')
        except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
                    __cnx.close()
    return __cnx