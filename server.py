from mysqlconnection import get_connection
import insert
import json
from flask import Flask,request,jsonify


app = Flask(__name__)
connection = get_connection()
@app.route('/insertdetails',methods=['POST'])
def insertdetails():
    request_payloads = json.loads(request.form['data'])
    return_id = insert.insert_details(connection,request_payloads)
    response = jsonify({
        'user_id':return_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__=="__main__":
    app.run(port=5000,debug=True)