from mysqlconnection import get_connection

def insert_details(connection,details):
    cursor = connection.cursor()
    query = ('INSERT INTO user_details(name,number,email,password) VALUES(%s,%s,%s,%s)')
    data = (details['name'],details['number'],details['email'],details['password'])
    cursor.execute(query,data)
    connection.commit()
    return cursor.lastrowid


if __name__ == "__main__":
    connection = get_connection()
    # details ={
    #     "name":"darshil",
    #     "number":"1234567890",
    #     "email":"darshil@gmail.com",
    #     "password":"darshil123
    # }
    # print(insert_details(connection,details))
    print("Connection is established")