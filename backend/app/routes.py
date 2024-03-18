from app import app,db
from flask import jsonify, request

from app.models import Subscribers
from threading import Thread
import time
import json

def frequency_scheduler():
    while True:
        _subscribers = Subscribers.query.all()
        for subscriber in _subscribers:
            time_now = time.time()
            if ((time_now - subscriber.last_update) >= subscriber.frequency_val or subscriber.last_update == 0):
                subscriber.send_update()

# Start the background process as a daemon thread
background_thread = Thread(target=frequency_scheduler)
background_thread.daemon = True
background_thread.start()


@app.route('/')
def index():
    return "Hello, World!"

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        data = request.get_json()
        _subscriber = Subscribers.query.filter_by(contact_value=data['contactValue']).first()
        if (_subscriber):
            _subscriber.stock_ticker = data['stockTicker']
            _subscriber.threshold = data['threshold']
            _subscriber.frequency_val = data['frequency_val']
            db.session.commit()
            stock_hist_json = json.dumps(_subscriber.get_stock_hist()['Close'].values.tolist())

            return jsonify({
                'message': 'Updated your profile stock. You will receive updates on your stock.',
                'stock_hist': stock_hist_json
            })
        else:
            _subscriber = Subscribers(data['contactType'], data['contactValue'], data['stockTicker'], data['threshold'], data['frequency_val'])
            db.session.add(_subscriber)
            db.session.commit()
            stock_hist_json = json.dumps(_subscriber.get_stock_hist()['Close'].values.tolist())

            return jsonify({
                'message': 'Added your profile stock. You will receive updates on your stock.',
                'stock_hist': stock_hist_json
            })