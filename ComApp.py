from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'company'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('companyform.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.tarc.edu.my')


@app.route("/companyform", methods=['GET', 'POST'])
def Company():
    # com_id = request.form['com_id']
    # com_pwd = request.form['com_pwd']
    com_name = request.form['com_name']
    com_address = request.form['com_address']
    com_HP = request.form['com_hp']
    com_email = request.form['com_mail']
    com_description = request.form['com_description']
    com_website = request.form['com_website']
    com_logo_file = request.files['company_logo_file']
    job_title = request.form['job_title']
    job_type = request.form['job_type']
    job_description = request.form['job_description']
    # status = request.form['com_id']
    


    insert_sql = "INSERT INTO company VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if com_logo_file.filename == "":
        return "Please select an image file"

    try:

        cursor.execute(insert_sql, (com_name, com_address, com_HP,com_email,com_description,com_website,job_title,job_type,job_description))
        db_conn.commit()
        # Uplaod image file in S3 #
        comp_image_file_name_in_s3 = str(com_name) + "_logo_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=comp_image_file_name_in_s3, Body=com_logo_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                comp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddComOutput.html', name=comp_name)
        #return to company profile page

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

