from os.path import abspath
from flask import Blueprint
from flask import render_template
import os ,sys
import json

from pyvis.network import Network
import pyvis.options
import pandas as pd
from werkzeug.utils import secure_filename

import numpy as np


from bokeh.io import show
from bokeh.models import BasicTicker, ColorBar, LinearColorMapper, PrintfTickFormatter, ColumnDataSource, Button
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import column, row
from bokeh.palettes import Greys256
from bokeh.models.callbacks import CustomJS
from bokeh.transform import linear_cmap


networkGraph = Blueprint('networkGraph', __name__)

@networkGraph.route('/network')
def network():
#find uploaded csv file name, save it as a var
    dirs = os.path.abspath('flaskr\static\csvs')
    file_list = os.listdir(dirs)
    csv_file = os.path.join(dirs, file_list[0])

    #create an object 
    net = Network()
  
    #create a dataframe
    #format the dataframe
    df = pd.read_csv(csv_file)
    #adds nodes and edges to the object net
    
    for e in range(len(df.index)):
        source = df.iloc[e]['fromId']
        target = df.iloc[e]['toId']

        label_source = df.iloc[e]['fromEmail']
        label_target = df.iloc[e]['toEmail']

        title_source = df.iloc[e]['fromJobtitle']
        title_target = df.iloc[e]['toJobtitle']

        edge_title = df.iloc[e]['date']


        net.add_node(int(source), label_source, title=title_source)
        net.add_node(int(target), label_target, title=title_target)
        net.add_edge(int(source), int(target), title = edge_title)
    

    for e in range(net.num_nodes()):
      if net.nodes[e]['title'] == 'Unknown':
        net.nodes[e]['group'] = '1'

      elif net.nodes[e]['title'] == 'Trader':
        net.nodes[e]['group'] = '2'
    
      elif net.nodes[e]['title'] == 'Vice President':
        net.nodes[e]['group'] = '3'

      elif net.nodes[e]['title'] == 'Employee':
        net.nodes[e]['group'] = '4'

      elif net.nodes[e]['title'] == 'Managing Director':
        net.nodes[e]['group'] = '5'
    
      elif net.nodes[e]['title'] == 'Manager':
        net.nodes[e]['group'] = '6'

      elif net.nodes[e]['title'] == 'President':
        net.nodes[e]['group'] = '7'

      elif net.nodes[e]['title'] == 'Director':
          net.nodes[e]['group'] = '8'    

      elif net.nodes[e]['title'] == 'CEO':
        net.nodes[e]['group'] = '9'

      elif net.nodes[e]['title'] == 'In House Lawyer':
        net.nodes[e]['group'] = '10'  


    
    # now we can acces the nodes dict and the edges dict
    # using net.nodes and net.edges

    # we need to make two .js files that contain
    # the nodes and the edges
    # we use json.dumps to convert the net.nodes and net.edges
    # dicts respectively

    # then the code below creates two files:
    # nodes.js and edges.js

    nodes_text = json.dumps(net.nodes)
    file = open(os.path.join(os.path.abspath('flaskr'), 'static/nodes.js'), 'w')
    file.write("nodes = " + nodes_text)
    file.close()
    
    edges_text = json.dumps(net.edges)
    file = open(os.path.join(os.path.abspath('flaskr'), 'static/edges.js'), 'w')
    file.write("edges = " + edges_text)
    file.close()
    
    # nodes.js and edges.js files are used in
    # the visualizations.html to show the nodes and the edges
    # the interactive part comes from javascript code and the
    # visJS library 

    # the code below renders the templates/visualizations.html file
    # and displays the webpage to the user

    return render_template("networkgraph.html")