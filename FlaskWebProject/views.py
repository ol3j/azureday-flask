"""
Routes and views for the flask application.
"""

from flask import Flask, render_template, request, url_for
from FlaskWebProject import app
from azure.storage.blob import BlobService
from azure.servicebus import ServiceBusService, Message
import uuid
import json
import os

service_keys = {
    'stor_acc_name': os.environ['STOR_ACC_NAME'],
    'stor_acc_key': os.environ['STOR_ACC_KEY'],
    'sb_acc_name': os.environ['SB_ACC_NAME'],
    'sb_acc_key': os.environ['SB_ACC_KEY'],
    'sb_namespace': os.environ['SB_NAMESP']
}

stor_acc_name = service_keys['stor_acc_name']
stor_acc_key = service_keys['stor_acc_key']
sb_acc_name = service_keys['sb_acc_name']
sb_acc_key = service_keys['sb_acc_key']
sb_namespace = service_keys['sb_namespace']


# storage
account_name = stor_acc_name
account_key = stor_acc_key
blob_service = BlobService(account_name, account_key)

#service bus
key_name = sb_acc_name
key_value = sb_acc_key
service_namespace = sb_namespace
sbs = ServiceBusService(service_namespace,
                        shared_access_key_name=key_name,
                        shared_access_key_value=key_value)

@app.route('/')
@app.route('/home')
def form():
    return render_template('form_submit.html')


@app.route('/hello/', methods=['POST'])
def hello():
    email = request.form['youremail']
    file = request.files['file']
    basename = file.filename
    suffix = uuid.uuid4().hex
    filename = '_'.join([suffix, basename])
    filedata = file.read()
    blob_service.put_block_blob_from_bytes(
        'images',
        filename,
        filedata
    )
    url = blob_service.make_blob_url(
    container_name='images',
    blob_name=filename,
    )
    body = json.dumps({'email': email, 'image': url})
    msg = Message(body)
    sbs.send_queue_message('azureday', msg)

    return render_template('form_action.html', email=email, url=url)