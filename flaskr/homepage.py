from flask import Blueprint
from flask import current_app
from flask import render_template
import numpy as np
import pandas as pd
import networkx as nx
import os

table_page = Blueprint('html_table', __name__)

@table_page.route('/') #initializes url
def enron_table(): #function which returns the table
    return render_template('index.html')
