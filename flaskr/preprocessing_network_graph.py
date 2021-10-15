import pandas as pd
import os
import json
from pyvis.network import Network


def preprocessing_network_graph():
        
    #create an object 
    net = Network()
            
    #create a dataframe
    #format the dataframe
    df = pd.read_csv(os.path.abspath('flaskr/static/csvs/csv_file.csv'))

    #adds nodes and edges to the object net
                
    for e in range(len(df.index)):
        source = df.iloc[e]['fromId']
        target = df.iloc[e]['toId']

        label_source = df.iloc[e]['fromEmail']
        label_target = df.iloc[e]['toEmail']

        title_source = df.iloc[e]['fromJobtitle']
        title_target = df.iloc[e]['toJobtitle']

        net.add_node(n_id=int(source), label= str(source), title=(label_source+'\n'+title_source), group=title_source, shape='circle')
        net.add_node(n_id=int(target), label= str(target), title=(label_target+'\n'+title_target), group=title_target, shape='circle')
        
        net.add_edge(int(source), int(target))

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
                    
