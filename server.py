import io
import datetime
import pytz
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask import Response
import base64

plt.style.use('seaborn')
sns.set(rc={'figure.figsize':(11, 4)})

app = Flask(__name__)

@app.route("/")
def home():
    column_names = ['ip', 'R1', 'fan-mode', 'R2', 'use-fan', 'R3', 'active-fan',
                    'R4', 'cpu-overtemp-check', 'R5', 'cpu-overtemp-threshold', 'R6',
                    'cpu-overtemp-startup-delay', 'R7', 'voltage', 'R8', 'current',
                    'R9', 'temperature', 'R10', 'cpu-temperature', 'R11',
                    'power-consumption', 'R12', 'psu1-state', 'R13', 'psu2-state',
                    'R14', 'fan1-speed', 'datetime']

    with open('router_health_data.csv', 'r') as f:
        df = pd.read_csv(f, names=column_names, parse_dates=True, index_col=29)

    df.drop(['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14'],
            axis=1, inplace=True)

    df['temperature'] = pd.to_numeric(df['temperature'].str[:-1])
    df['cpu-temperature'] = pd.to_numeric(df['cpu-temperature'].str[:-1])

    timezone = pytz.timezone('America/Sao_Paulo')
    now = timezone.localize(datetime.datetime.now()).strftime('%Y-%m-%d %H:%M')
    yesterday = timezone.localize((datetime.datetime.now() - datetime.timedelta(days=1))).strftime('%Y-%m-%d %H:%M')

    fig, ax = plt.subplots(6, 1, figsize=(14, 14))
    plt.subplots_adjust(hspace=1)
    plt.locator_params(axis='y', nbins=6)

    ax[0].plot(df.loc[yesterday:now, 'voltage'])
    ax[0].set_title('Voltagem', fontsize=12)
    ax[1].plot(df.loc[yesterday:now, 'current'])
    ax[1].set_title('Corrente', fontsize=12)
    ax[2].plot(df.loc[yesterday:now, 'power-consumption'])
    ax[2].set_title('Consumo', fontsize=12)
    ax[3].plot(df.loc[yesterday:now, 'temperature'])
    ax[3].set_title('Temperatura', fontsize=12)
    ax[4].plot(df.loc[yesterday:now, 'cpu-temperature'])
    ax[4].set_title('Temperatura Processador', fontsize=12)
    ax[5].plot(df.loc[yesterday:now, 'fan1-speed'])
    ax[5].set_title('Velocidade Cooler', fontsize=12)

    for x in range(6):
        ax[x].xaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax[x].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'));
        ax[x].yaxis.set_major_locator(plt.MaxNLocator(6))

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(output.getvalue()).decode('utf8')

    return render_template("index.html", image=pngImageB64String)

    return Response(output.getvalue(), mimetype='image/png')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
