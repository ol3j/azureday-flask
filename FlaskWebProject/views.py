"""
Routes and views for the flask application.
"""

from flask import Flask, render_template, request, url_for
from FlaskWebProject import app
from azure.storage.blob import BlobService
from azure.storage.queue import QueueService
import uuid
import json
import os

service_keys = {
    'stor_acc_name': os.environ['STOR_ACC_NAME'],
    'stor_acc_key': os.environ['STOR_ACC_KEY']
}

stor_acc_name = service_keys['stor_acc_name']
stor_acc_key = service_keys['stor_acc_key']



# storage
account_name = stor_acc_name
account_key = stor_acc_key
blob_service = BlobService(account_name, account_key)
queue_service = QueueService(account_name=stor_acc_name, account_key=stor_acc_key)
queue_service.create_queue('taskqueue')

@app.route('/')
@app.route('/home')
def form():
    return render_template('form_submit.html')


@app.route('/hello/', methods=['POST'])
def hello():
    mobile = request.form['yourmobile']
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
    body = json.dumps({'mobile': mobile, 'image': url})
    queue_service.put_message('taskqueue', body)

    return render_template('form_action.html', mobile=mobile, url=url)