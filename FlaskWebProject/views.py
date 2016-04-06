"""
Routes and views for the flask application.
"""

from flask import Flask, render_template, request, url_for
from FlaskWebProject import app
from azure.storage.blob import BlobService
from azure.storage.queue import QueueService
from azure.storage.table import TableService, Entity
from applicationinsights import TelemetryClient
import uuid
import json
import os
import redis
from random import randint


service_keys = {
    'stor_acc_name': os.environ['STOR_ACC_NAME'],
    'stor_acc_key': os.environ['STOR_ACC_KEY'],
    'redis_pass': os.environ['REDIS_PASS'],
    'redis_server': os.environ['REDIS_SERVER'],
    'instr_key': os.environ['INSTR_KEY']
    }

stor_acc_name = service_keys['stor_acc_name']
stor_acc_key = service_keys['stor_acc_key']
redis_pass = service_keys['redis_pass']
redis_server = service_keys['redis_server']
instr_key = service_keys['instr_key']


# storage
account_name = stor_acc_name
account_key = stor_acc_key
blob_service = BlobService(account_name, account_key)
blob_service.create_container('images')
queue_service = QueueService(account_name, account_key)
queue_service.create_queue('taskqueue')
table_service = TableService(account_name, account_key)
table_service.create_table('tasktable')


r = redis.StrictRedis(host=redis_server, port=6380, db=0, password=redis_pass, ssl=True)

tc = TelemetryClient(instr_key)

@app.route('/')
@app.route('/home')
def form():
    # instance = os.getenv('WEBSITE_INSTANCE_ID', 0)
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
    body = json.dumps({'suffix': str(suffix), 'image': str(url)})
    queue_service.put_message('taskqueue', body)
    task = {'PartitionKey': 'tasksPoznan', 'RowKey': suffix, 'mobile' : mobile, 'file' : filename}
    table_service.insert_entity('tasktable', task)
    r.set(suffix, mobile)
    important_metric = randint(0,9)
    tc.track_metric('important metric', important_metric, { 'App': 'PozTest', 'Version': 'staging' })
    tc.flush()

    return render_template('form_action.html', mobile=mobile, url=url, important_metric=important_metric)
