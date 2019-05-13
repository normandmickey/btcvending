from flask import Flask, request, render_template, jsonify
from btcpay import BTCPayClient
import pickle
import serialized_redis
import time
import pyqrcode
import io
import os

INVOICE_FOLDER = os.path.join('static', 'invoice_folder')

app = Flask(__name__)
app.config['INVOICE_FOLDER'] = INVOICE_FOLDER

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/invoice')
def invoice():
#    return "BTC Lightning"

    r = serialized_redis.PickleSerializedRedis(host='localhost', port=6379, db=0)
#   client = BTCPayClient.create_client(host='https://lunanode1.lightninginabox.co', code='uJ4S4D9')

#   r.set('client', client)

    btcpayclient = r.get('client')

    new_invoice = btcpayclient.create_invoice({"price": 0.01, "currency": "USD"})
    new_invoice_id = new_invoice['id']

    invoice_status = 'new'
    while invoice_status != 'completed':

        fetched_invoice = btcpayclient.get_invoice(new_invoice_id)
        invoice_status = fetched_invoice['status']
        lightning_invoice = fetched_invoice['addresses']['BTC_LightningLike']

#        print(invoice_status)
#        print(lightning_invoice)

        lninvoice =  pyqrcode.create(lightning_invoice)
        full_filename = os.path.join(app.config['INVOICE_FOLDER'], 'lninvoice.svg')
        lninvoice.svg(full_filename, scale=4)
        buffer = io.BytesIO()
        lninvoice.svg(buffer)
        return render_template('invoice.html', invoice_image = full_filename)
#        print(text.terminal())

    else:
        print(invoice_status)

        time.sleep(4)
        quit()

# getInvoice(0.01)

@app.route('/process',methods= ['POST'])
def process():
  firstName = request.form['firstName']
  lastName = request.form['lastName']
  output = firstName + lastName
  if firstName and lastName:
   return jsonify({'output':'Full Name: ' + output})
  return jsonify({'error' : 'Missing data!'})
