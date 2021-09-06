from flask import Flask
from .homepage import table_page
from .csv_input import upload
from .networkGraph import networkGraph
from .heatmap import heatmap
from .bar_graph import bargraph
from .bothgraphs import multiplegraphs
import os

#defines function to create flask instance
def create_app():
    #creates object Flask and tells the app the instace folder
    app = Flask(__name__, instance_relative_config=True)

    #top file name
    TOP_FILE = 'flaskr'

    #variable root dir
    ROOT_PATH = os.path.abspath(TOP_FILE)

    #designates folder where upload files are stored
    UPLOAD_FOLDER = os.path.join(ROOT_PATH, 'static\csvs')
    #sets the upload folder in the app config
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    #registers blueprints
    app.register_blueprint(upload, url_prefix='/')
    app.register_blueprint(table_page, url_prefix='/')
    app.register_blueprint(heatmap, url_prefix='/')
    app.register_blueprint(networkGraph, url_prefix='/')
    app.register_blueprint(bargraph, url_prefix='/')
    app.register_blueprint(multiplegraphs, url_prefix='/')
    return app


# This code does not work
#@app.route('/vis')
#def vis():
#    G = nx.Graph()
#    G = nx.from_pandas_edgelist(df_enron, 'fromId', 'toId')
#    figure(figsize=(10, 8))
#    nx.draw_shell(G, with_labels=True)


