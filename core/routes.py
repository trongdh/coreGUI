from core import app
from flask import Flask, render_template, jsonify, request
from core.models import Item
import pandas as pd
from collections import OrderedDict

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/kpi')
def kpi_page():
    return render_template('kpi.html')


@app.route('/get_data', methods=['POST'])
def get_data():
    periodSelect = request.form['periodSelect']
    df = pd.read_csv(r'kpi/output/' + periodSelect + '.csv')
    df['Start_time'] = pd.to_datetime(df['Start_time'], format="%Y%m%d%H%M")
    df['End_time'] = pd.to_datetime(df['End_time'], format="%Y%m%d%H%M")
    columns = df.columns.tolist()
    data = df.values.tolist()
    return jsonify({'columns': columns, 'data': data})



@app.route('/setting')
def setting_page():
    items = [
        {'node': 'SIMS01', 'time': '2022-12-08 00:00',
            'lusr': '99.98', 'ausr': '99.60', 'psr': '95.6'},
        {'node': 'SIMS02', 'time': '2022-12-08 00:00',
            'lusr': '99.97', 'ausr': '99.61', 'psr': '94.6'},
        {'node': 'TRMS01', 'time': '2022-12-08 00:00',
            'lusr': '99.96', 'ausr': '99.62', 'psr': '93.6'}
    ]
    return render_template('setting.html', items=items)
