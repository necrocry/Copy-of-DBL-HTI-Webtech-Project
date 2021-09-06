import datetime
from os.path import abspath
from bokeh.core.enums import SizingMode
from bokeh.models.tools import Tap
from flask import Blueprint
from flask import render_template, request
import os ,sys
import json
import time, threading
from pyvis.network import Network
import pyvis.options
import pandas as pd
from werkzeug.utils import secure_filename
import numpy as np
import re
from datetime import datetime


from bokeh.io import show
from bokeh.models import BasicTicker, ColorBar, LinearColorMapper, PrintfTickFormatter, ColumnDataSource, Button, BoxAnnotation, Slider
from bokeh.plotting import figure
from bokeh.embed import components, json_item
from bokeh.layouts import column, row
from bokeh.palettes import Greys256, Viridis256
from bokeh.models.callbacks import CustomJS
from bokeh.transform import linear_cmap
from .preprocessing_network_graph import preprocessing_network_graph

from bokeh.models.annotations import ColorBar, Label
from bokeh.models.mappers import ColorMapper
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import FactorRange
from bokeh.models import ColumnDataSource, CheckboxButtonGroup, CustomJS
from bokeh.transform import factor_cmap
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.transform import linear_cmap
from bokeh.palettes import Viridis256


multiplegraphs = Blueprint('multiplegraphs', __name__)

@multiplegraphs.route('/both')
def multiple():
#find uploaded csv file name, save it as a var
  preprocessing_network_graph()
  #Heatmap code


  #create a dataframe from CSV file
  csv_path = os.path.join(os.path.abspath('flaskr'), 'static\csvs\csv_file.csv')
  #csv_path = r'C:\Users\Admin\Documents\TUe\DBL HTI\enron-v1.csv'    LOCAL
  enron_csv = pd.read_csv(csv_path,parse_dates=['date'])


  #create dataframe with fromId and toId
  df_id = enron_csv[['fromId', 'toId', 'messageType', 'date']]

  #sort pd_id by fromId and toId and reset index
  df_id = df_id.sort_values(by=['fromId', 'toId'])
  df_id = df_id.reset_index(drop=True)



  #create a list with all id
  id_list = df_id['fromId'].tolist()
  for i in df_id['toId'].tolist():
      id_list.append(i)

  id_list = list( dict.fromkeys(id_list))
  id_list.sort()


  #make id list with strings
  id_list_string = [str(x) for x in id_list]

  #make array filled with 0's
  zero_square = np.zeros(shape=(len(id_list),len(id_list)))

  #add zero square to dataframe
  df_id_square = pd.DataFrame(zero_square, index= id_list, columns = id_list)
  df_id_square_TO = df_id_square.copy()


  #fill the dataframe pd_id_heat with the number of mails fromId, toId
  for i in range(0,len(df_id)):
      df_id_square.loc[df_id['fromId'][i]][df_id['toId'][i]] = df_id_square.loc[df_id['fromId'][i]][df_id['toId'][i]] + 1
      if df_id['messageType'][i] == 'TO':
          df_id_square_TO.loc[df_id['fromId'][i]][df_id['toId'][i]] = df_id_square_TO.loc[df_id['fromId'][i]][df_id['toId'][i]] + 1


  #reform the both dataframes
  df_id_square['fromId'] = id_list_string
  df_id_square = df_id_square.set_index('fromId')
  df_id_square.columns.name = 'toId'

  df_id_square_TO['fromId'] = id_list_string
  df_id_square_TO = df_id_square_TO.set_index('fromId')
  df_id_square_TO.columns.name = 'toId'



  #make new dataframe ['toId', 'fromId', 'size']
  df_data = pd.DataFrame(df_id_square.stack(), columns=['size']).reset_index()
  df_data_cc = pd.DataFrame(df_id_square_TO.stack(), columns=['sizeNoCC']).reset_index()
  df_data['sizeNoCC'] = df_data_cc['sizeNoCC']


  """
  for i in range(0,len(df_data)):
  if df_data['size'][i] > 0:
  fromId = df_data['fromId'][i]
  toId = df_data['toId'][i]
  print([enron_csv['fromId'] == fromId])
  #index1 = enron_csv[((enron_csv['toId'] == toId) & (enron_csv['fromId'] == fromId))].index()
  index1 = ((enron_csv['toId'] == toId) & (enron_csv['fromId'] == fromId))
  print(index1)
  #df_data['date'][i] = enron_csv['date'].loc[index]
  #df_data['date'] = enron_csv[''] 
  """

  #make lists of fromId and toId
  fromId_list = list(df_id_square.index)

  """
  !
  this way of no zero is going to give errors when using sizeNoCC
  !
  """

  #create a dataframe without size 0
  df_nozero = df_data[df_data['size'] !=0].copy()


  #colour mapper
  colors = ["#FFFFFF","#FBF3F3","#F7E8E8","#F3DCDC","#F0D0D0","#ECC5C5","#E8B9B9","#E4ADAD","#E0A2A2","#DC9696","#D98A8A","#D57E7E","#D17373","#CD6767","#C95B5B","#C55050","#C24444","#BE3838","#BA2D2D","#B62121"]
  mapper = LinearColorMapper(palette=Greys256[::-1], low=df_nozero['size'].quantile(0.10), high=df_nozero['size'].quantile(0.95))
  mappertest = linear_cmap(field_name='size', palette=Greys256[::-1], low=df_nozero['size'].quantile(0.10), high=df_nozero['size'].quantile(0.95))
  mapperNoCC = LinearColorMapper(palette=colors, low=df_nozero['sizeNoCC'].quantile(0.10), high=df_nozero['sizeNoCC'].quantile(0.95))


  #make the figure 
  heatmap_figure = figure(title= 'Mail traffic'.format(fromId_list[0], fromId_list[-1]),
              x_axis_location = 'above', tools = 'hover,save,pan,box_zoom,reset,wheel_zoom,tap' , plot_width= 1000, plot_height=1000, sizing_mode="scale_both",
              x_range= fromId_list, y_range= fromId_list, 
              tooltips=[('Id: from-to', '@fromId @toId'), ('size', '@size'), ('sizeNoCC', '@sizeNoCC')])
  
  

  #create a string to change the font size
  length_list = 0
  for i in id_list:
      length_list += 1

  #determines which size the font should be for x people sending mails
  if length_list < 10:
      font_variable = '30px'
  elif length_list <50:
      font_variable = '10px'
  elif length_list < 100:
      font_variable = '5px'
  elif length_list < 160:
      font_variable = '4px'
  else: font_variable = '0px'
  

  heatmap_figure.grid.grid_line_color = None
  heatmap_figure.axis.axis_line_color = None
  heatmap_figure.axis.major_tick_line_color = None
  heatmap_figure.axis.major_label_text_font_size = font_variable
  heatmap_figure.axis.major_label_standoff = 10

  #create a dataframe with strings for all id's 
  df_Id_string = pd.DataFrame(id_list_string)
  df_Id_string.columns = ['fromId']
  df_Id_string['size'] = df_nozero['size']

  toId_list_complete = df_data['toId'].tolist()
  toId_list_complete_string = [str(int) for int in toId_list_complete]
  df_data.drop(columns=['toId'], inplace=True)
  df_data['toId'] = toId_list_complete_string


  #add figure to rect
  source = ColumnDataSource(df_data)
  heatmap_all = heatmap_figure.rect(x ='fromId', y ='toId', width = 1, height = 1, source = source, 
  nonselection_fill_alpha = 1.0, fill_color=mappertest, line_color=None)
  
  color_bar = ColorBar(color_mapper=mappertest["transform"], label_standoff=12)
  
  heatmap_figure.add_layout(color_bar, 'right')
  #heatmap_TO = heatmap_figure.rect(x ='fromId', y ='toId', width = 1, height = 1, source = source, fill_color={'field': 'sizeNoCC', 'transform': mapper},
  #line_color=None)

  #heatmap_TO.visible = False
  type_button = Button(label='Change CC', button_type='success')
  
  callback = CustomJS(args=dict(heatmap_all=heatmap_all, source = source, Greys256=Greys256, low=df_nozero['size'].quantile(0.10), high=df_nozero['size'].quantile(0.95), linear_map=mappertest), code="""
      var color_mapper = linear_map;
      var data = source.data;
      var i = data['size'];
      var sizeNoCC = data['sizeNoCC'];
      console.log(color_mapper.field)
      if (color_mapper.field === 'size') {
          color_mapper.field = 'sizeNoCC';
          heatmap_all.glyph.fill_color = color_mapper;
      }
      else if (color_mapper.field === "sizeNoCC") {
          color_mapper.field = 'size';
          heatmap_all.glyph.fill_color = color_mapper;
      }
      source.change.emit();
      """)

  type_button.js_on_click(callback)
  """
  date_slider= DateRangeSlider(value=(enron_csv['date'].min(), enron_csv['date'].max()),start= enron_csv['date'].min(), end= enron_csv['date'].max())
  

  date_slider.js_on_change("value", CustomJS(code = '''
    
  
  '''))
  """
  #add boxAnnotation
  highlightRow = BoxAnnotation(top=0,bottom=0,fill_alpha=0, fill_color="#00FF00")
  highlightColumn = BoxAnnotation(left=0,right=0,fill_alpha=0, fill_color="#00FF00")
  heatmap_figure.add_layout(highlightRow)
  heatmap_figure.add_layout(highlightColumn)
  heatmap_figure.tags = ['true', 10]
  
  #callback for highlighting the selected row
  callback_highlight= CustomJS(args=dict(source=source, length_list=length_list, id_list=id_list, heatmap_figure=heatmap_figure, highlightRow=highlightRow, highlightColumn=highlightColumn), code="""
      var highlightRow = highlightRow;
      var highlightColumn = highlightColumn;
      var inds = source.selected.indices
      var element_nr = 0;
      var heatmap_figure = heatmap_figure;
      var i;
      var id = -1;
      i+=1;
      if(id == -1){
        while(inds >= length_list){
          element_nr += 1;
          inds = inds - length_list;
        }
        id = id_list[element_nr];
      }
      else{
        while(selectedNode != id_list[element_nr]){
          element_nr += 1;
        }          
      }
      setInterval(myFunction,10);
      function myFunction() {
        if(update == 'True'){
          console.log(update);
          element_nr = 0;
          while(selectedNode != id_list[element_nr]){
          element_nr += 1;
          } 
          highlightRow.top = element_nr+1;
          highlightRow.bottom = element_nr;
          highlightRow.fill_alpha = 0.1;
          highlightColumn.right = element_nr+1;
          highlightColumn.left = element_nr;
          highlightColumn.fill_alpha = 0.1;;
          update = 'False';
        }
      }
      highlightRow.top = element_nr+1;
      highlightRow.bottom = element_nr;
      highlightRow.fill_alpha = 0.1;
      highlightColumn.right = element_nr+1;
      highlightColumn.left = element_nr;
      highlightColumn.fill_alpha = 0.1;

      
      set_id_heatmap(id);
      neighbourhoodHighlight();
      source.change.emit();
  """
  )


  source.selected.js_on_change("indices", callback_highlight)
  #test_button = Button(label='test', button_type='success')
  #test_button.js_on_click(callback_highlight)
  #print(source.data)
  layout = column(column([type_button, heatmap_figure]), sizing_mode="scale_both")
  
  item_text = json.dumps(json_item(layout, "myplot"))
  file = open(os.path.join(os.path.abspath('flaskr'), 'static/layout.js'), 'w')
  file.write(item_text)
  file.close()
  
  script, div = components(layout)
  #File input
  df_csv = pd.read_csv(csv_path,parse_dates=['date'])
  df_csv['year'] = pd.DatetimeIndex(df_csv['date']).year                                                      #Extracts only the year from the date

  #Dataframe filters and groupings
  df_filter = df_csv[['fromJobtitle', 'toJobtitle', 'year', 'sentiment']]                                                  #Extracts these 3 columns
  df_filter['year'] = df_filter['year'].astype(str)                                                           #Sets 'year' as String
  df_filter = df_filter.groupby(df_filter.columns.tolist(),as_index=False).size()                             #Count how many emails sent
  print(df_filter.columns.tolist())
  df_final = df_filter.groupby(['fromJobtitle', 'year'], as_index = False).sum()            

  df_final['x'] = df_final[['fromJobtitle', 'year']].apply(lambda x: (x[0],str(x[1])), axis=1)                 #Group data by year and job title
  df_label = df_filter.groupby(['year'], as_index = False).sum() 
  

  #Create color map for sentiment
  sentiment_mapper = linear_cmap(field_name='sentiment', palette=Viridis256 ,low=df_final['sentiment'].min() ,high=df_final['sentiment'].max())
  
  #create colorbar
  sentiment_colorbar = ColorBar(color_mapper=sentiment_mapper['transform'], label_standoff=12)
  #Plot the bar graph

  TOOLTIPS = [
      ("Function and year", "@x"),
      ("Number of people with this job", "@size"),
  ]
  
  


  LABELS = df_label['year'].unique().tolist()
  #active labels
  active_LABELS=[]
  i=0
  while i < len(LABELS):
      active_LABELS.append(i)
      i += 1


  checkbox_group = CheckboxButtonGroup(labels=LABELS, active=active_LABELS)

  
  

  source = ColumnDataSource(df_final)
  all_source = ColumnDataSource(df_final)

  p = figure(
      x_range=FactorRange(*(df_final["x"])),
      width=1400,
      tooltips= TOOLTIPS,
      title="Emails sent by each jobtitle each year",
      tools = 'hover,save,pan,box_zoom,reset,wheel_zoom'
  )


  p.vbar(
      x="x",
      top="size",
      width=0.9,
      source=source,
      fill_color=sentiment_mapper
  )

  bar_callback = CustomJS(args=dict(source=source, all_source=all_source, labels=LABELS), code="""
      var all_data = all_source.data;
      var old_data = source.data;
      var labels = labels;
      var active = this.active;
      var drop = [];
      var i;
      var j;
      var k;
      var list_drop = [];
      var jsonDrop =[];
      let dropIndices;
      var nonDrop = [];
      var lengthArray = [];

      old_data['year'] = [... all_data['year']];
      old_data['sentiment'] = [... all_data['sentiment']];
      old_data['fromJobtitle'] = [... all_data['fromJobtitle']];
      old_data['x'] = [... all_data['x']];
      old_data['index'] = [... all_data['index']];
      old_data['size'] = [... all_data['size']];

      for(i=0; i < labels.length; i++){  
          if(active.indexOf(i) == -1){
              drop.push(i);
          }
          lengthArray.push(i);
      }    
      for(i=0; i < drop.length; i++){
          list_drop.push(labels[drop[i]]);
      }
      
      for(j=0; j < list_drop.length; j++){
          for(i=0; i < old_data.year.length; i++){
              if(old_data.year.indexOf(list_drop[j], i) != -1){
                  jsonDrop.push(old_data.year.indexOf(list_drop[j], i));
              }
          }
      }

      dropIndices = [...new Set(jsonDrop)];
      dropIndices.sort(function(a,b){
          return a-b;
      });

      for(i=0; i < lengthArray.length; i++){
          for(j=0; j < drop.length; j++){
              if(lengthArray[i] == drop[j]){
                  nonDrop.push(lengthArray.splice(drop[i], 1));
              }
          }
      }

      var tempSent = Array.from(old_data['sentiment']);
      
      

      for(i=0; i < dropIndices.length; i++){
          old_data['year'].splice(dropIndices[i] - i,1);
          old_data['fromJobtitle'].splice(dropIndices[i]- i, 1);
          old_data['size'].splice(dropIndices[i]- i, 1);
          old_data['x'].splice(dropIndices[i]- i, 1);
          old_data['index'].splice(dropIndices[i]- i, 1);
          tempSent.splice(dropIndices[i]- i, 1);
      }

      var tempSent64 = new Float64Array(tempSent);
      old_data['sentiment'] = [... tempSent64];

      console.log(labels);
      console.log(all_data);
      console.log(this.active);
      console.log(drop);
      console.log(list_drop);
      console.log(dropIndices);
      console.log(old_data);
      source.change.emit();
      """)
              
  checkbox_group.js_on_click(bar_callback)
              


  #add colorbar to p
  p.add_layout(sentiment_colorbar, 'right')

  layout_bar = column(column([checkbox_group, p], sizing_mode = 'scale_width'),sizing_mode = 'scale_both')
      
  script2, div2 = components(layout_bar)
  return render_template("FormBothGraphs.html", div=div,script=script, div2=div2,script2=script2)

@multiplegraphs.route('/both_filter/', methods = ['POST'])
def data():
  if request.method == 'GET':
    return f"The URL /data is accessed directly. Try going to '/form_both' to submit form"


  if request.method == 'POST':
     
    
    # Get the dates from the form,
    start_date = request.form.get("date1")
    end_date = request.form.get("date2")

    #Format the dates
    start_date = pd.Timestamp(re.sub('[-]', ', ', start_date))
    end_date = pd.Timestamp(re.sub('[-]', ', ', end_date))

    #create a dataframe from CSV file
    csv_path = os.path.join(os.path.abspath('flaskr'), 'static\csvs\csv_file.csv')
  #csv_path = r'C:\Users\Admin\Documents\TUe\DBL HTI\enron-v1.csv'    LOCAL
    df = pd.read_csv(csv_path,parse_dates=['date'])

    # create an object
    net = Network()

    # format the dataframe
    df = df.sort_values("date")
    df = df.reset_index(drop=True)

    for i in range(0, len(df.index)):
      if df['date'][i] >= start_date:
        break

    for j in range(len(df.index)-1, 0, -1):
      if df['date'][j] <= end_date:
        break

        
    df = df[i:j+1]
                
    # since json.dumps cannot dump a datetime object,
    # we reverse parse_dates
    df['date'] = df['date'].apply(lambda x: datetime.strftime(x, '%Y-%m-%d'))
    # adds nodes and edges to the object net
    for e in range(len(df.index)):
      source = df.iloc[e]['fromId']
      target = df.iloc[e]['toId']

      label_source = df.iloc[e]['fromEmail']
      label_target = df.iloc[e]['toEmail']

      title_source = df.iloc[e]['fromJobtitle']
      title_target = df.iloc[e]['toJobtitle']

      edge_title = df.iloc[e]['date']

      net.add_node(n_id=int(source), label= str(source), title=(label_source+'\n'+title_source), group=title_source, shape='circle')
      net.add_node(n_id=int(target), label= str(target), title=(label_target+'\n'+title_target), group=title_target, shape='circle')
      net.add_edge(int(source), int(target))
  
    edges_text = json.dumps(net.edges)
    file = open(os.path.abspath("flaskr/static/edges1.js"), "w")
    file.write("edges1 = " + edges_text)
    file.close()

    nodes_text = json.dumps(net.nodes)
    file = open(os.path.abspath("flaskr/static/nodes1.js"), "w")
    file.write("nodes1 = " + nodes_text)
    file.close()






    # Heatmap code
 
    #create dataframe with fromId and toId
    df_id = df[['fromId', 'toId', 'messageType', 'date']]


    #create a dataframe from CSV file
    #csv_path = os.path.join(os.path.abspath('flaskr'), 'static\csvs\csv_file')
    #csv_path = r'C:\Users\Admin\Documents\TUe\DBL HTI\enron-v1.csv'    LOCAL
    #enron_csv = pd.read_csv(csv_path,parse_dates=['date'])


    #create dataframe with fromId and toId
    #df_id = df[['fromId', 'toId', 'messageType', 'date']]

    #sort pd_id by fromId and toId and reset index
    df_id = df_id.sort_values(by=['fromId', 'toId'])
    df_id = df_id.reset_index(drop=True)



    #create a list with all id
    id_list = df_id['fromId'].tolist()
    for i in df_id['toId'].tolist():
        id_list.append(i)

    id_list = list( dict.fromkeys(id_list))
    id_list.sort()


    #make id list with strings
    id_list_string = [str(x) for x in id_list]

    #make array filled with 0's
    zero_square = np.zeros(shape=(len(id_list),len(id_list)))

    #add zero square to dataframe
    df_id_square = pd.DataFrame(zero_square, index= id_list, columns = id_list)
    df_id_square_TO = df_id_square.copy()


    #fill the dataframe pd_id_heat with the number of mails fromId, toId
    for i in range(0,len(df_id)):
        df_id_square.loc[df_id['fromId'][i]][df_id['toId'][i]] = df_id_square.loc[df_id['fromId'][i]][df_id['toId'][i]] + 1
        if df_id['messageType'][i] == 'TO':
            df_id_square_TO.loc[df_id['fromId'][i]][df_id['toId'][i]] = df_id_square_TO.loc[df_id['fromId'][i]][df_id['toId'][i]] + 1


    #reform the both dataframes
    df_id_square['fromId'] = id_list_string
    df_id_square = df_id_square.set_index('fromId')
    df_id_square.columns.name = 'toId'

    df_id_square_TO['fromId'] = id_list_string
    df_id_square_TO = df_id_square_TO.set_index('fromId')
    df_id_square_TO.columns.name = 'toId'



    #make new dataframe ['toId', 'fromId', 'size']
    df_data = pd.DataFrame(df_id_square.stack(), columns=['size']).reset_index()
    df_data_cc = pd.DataFrame(df_id_square_TO.stack(), columns=['sizeNoCC']).reset_index()
    df_data['sizeNoCC'] = df_data_cc['sizeNoCC']


    """
    for i in range(0,len(df_data)):
    if df_data['size'][i] > 0:
    fromId = df_data['fromId'][i]
    toId = df_data['toId'][i]
    print([enron_csv['fromId'] == fromId])
    #index1 = enron_csv[((enron_csv['toId'] == toId) & (enron_csv['fromId'] == fromId))].index()
    index1 = ((enron_csv['toId'] == toId) & (enron_csv['fromId'] == fromId))
    print(index1)
    #df_data['date'][i] = enron_csv['date'].loc[index]
    #df_data['date'] = enron_csv[''] 
    """

    #make lists of fromId and toId
    fromId_list = list(df_id_square.index)

    """
    !
    this way of no zero is going to give errors when using sizeNoCC
    !
    """
    #create a dataframe without size 0
    df_nozero = df_data[df_data['size'] !=0].copy()
    #colour mapper
    colors = ["#FFFFFF","#FBF3F3","#F7E8E8","#F3DCDC","#F0D0D0","#ECC5C5","#E8B9B9","#E4ADAD","#E0A2A2","#DC9696","#D98A8A","#D57E7E","#D17373","#CD6767","#C95B5B","#C55050","#C24444","#BE3838","#BA2D2D","#B62121"]
    mapper = LinearColorMapper(palette=Greys256[::-1], low=df_nozero['size'].quantile(0.10), high=df_nozero['size'].quantile(0.95))
    mappertest = linear_cmap(field_name='size', palette=Greys256[::-1], low=df_nozero['size'].quantile(0.10), high=df_nozero['size'].quantile(0.95))
    mapperNoCC = LinearColorMapper(palette=colors, low=df_nozero['sizeNoCC'].quantile(0.10), high=df_nozero['sizeNoCC'].quantile(0.95))
    #make the figure 
    heatmap_figure = figure(title= 'Mail traffic'.format(fromId_list[0], fromId_list[-1]),
                x_axis_location = 'above', tools = 'hover,save,pan,box_zoom,reset,wheel_zoom,tap' , plot_width= 1000, plot_height=1000, sizing_mode="scale_both",
                x_range= fromId_list, y_range= fromId_list, 
                tooltips=[('Id: from-to', '@fromId @toId'), ('size', '@size'), ('sizeNoCC', '@sizeNoCC')])
    
    
    #create a string to change the font size
    length_list = 0
    for i in id_list:
        length_list += 1
    #determines which size the font should be for x people sending mails
    if length_list < 10:
        font_variable = '30px'
    elif length_list <50:
        font_variable = '10px'
    elif length_list < 100:
        font_variable = '5px'
    elif length_list < 160:
        font_variable = '4px'
    else: font_variable = '0px'
    
    heatmap_figure.grid.grid_line_color = None
    heatmap_figure.axis.axis_line_color = None
    heatmap_figure.axis.major_tick_line_color = None
    heatmap_figure.axis.major_label_text_font_size = font_variable
    heatmap_figure.axis.major_label_standoff = 10
    heatmap_figure.xaxis.axis_label = "Mails sent from ID"
    heatmap_figure.yaxis.axis_label = "Mails sent to ID"
    #create a dataframe with strings for all id's 
    df_Id_string = pd.DataFrame(id_list_string)
    df_Id_string.columns = ['fromId']
    df_Id_string['size'] = df_nozero['size']
    toId_list_complete = df_data['toId'].tolist()
    toId_list_complete_string = [str(int) for int in toId_list_complete]
    df_data.drop(columns=['toId'], inplace=True)
    df_data['toId'] = toId_list_complete_string
    #add figure to rect
    source = ColumnDataSource(df_data)
    heatmap_all = heatmap_figure.rect(x ='fromId', y ='toId', width = 1, height = 1, source = source, 
    nonselection_fill_alpha = 1.0, fill_color=mappertest, line_color=None)
    
    color_bar = ColorBar(color_mapper=mappertest["transform"], label_standoff=12)
    
    heatmap_figure.add_layout(color_bar, 'right')
    #heatmap_TO = heatmap_figure.rect(x ='fromId', y ='toId', width = 1, height = 1, source = source, fill_color={'field': 'sizeNoCC', 'transform': mapper},
    #line_color=None)
    #heatmap_TO.visible = False
    type_button = Button(label='Change CC', button_type='success')
    
    callback = CustomJS(args=dict(heatmap_all=heatmap_all, source = source, Greys256=Greys256, low=df_nozero['size'].quantile(0.10), high=df_nozero['size'].quantile(0.95), linear_map=mappertest), code="""
        var color_mapper = linear_map;
        var data = source.data;
        var i = data['size'];
        var sizeNoCC = data['sizeNoCC'];
        console.log(color_mapper.field)
        if (color_mapper.field === 'size') {
            color_mapper.field = 'sizeNoCC';
            heatmap_all.glyph.fill_color = color_mapper;
        }
        else if (color_mapper.field === "sizeNoCC") {
            color_mapper.field = 'size';
            heatmap_all.glyph.fill_color = color_mapper;
        }
        source.change.emit();
        """)

    type_button.js_on_click(callback)
    """
    date_slider= DateRangeSlider(value=(enron_csv['date'].min(), enron_csv['date'].max()),start= enron_csv['date'].min(), end= enron_csv['date'].max())
    

    date_slider.js_on_change("value", CustomJS(code = '''
     
    
    '''))
    """
    #add boxAnnotation
    highlightRow = BoxAnnotation(top=0,bottom=0,fill_alpha=0, fill_color="#00FF00")
    highlightColumn = BoxAnnotation(left=0,right=0,fill_alpha=0, fill_color="#00FF00")
    heatmap_figure.add_layout(highlightRow)
    heatmap_figure.add_layout(highlightColumn)
    heatmap_figure.tags = ['true', 10]
    
    #callback for highlighting the selected row
    callback_highlight= CustomJS(args=dict(source=source, length_list=length_list, id_list=id_list, heatmap_figure=heatmap_figure, highlightRow=highlightRow, highlightColumn=highlightColumn), code="""
        var highlightRow = highlightRow;
        var highlightColumn = highlightColumn;
        var inds = source.selected.indices
        var element_nr = 0;
        var heatmap_figure = heatmap_figure;
        var i;
        var id = -1;
        i+=1;
        if(id == -1){
          while(inds >= length_list){
            element_nr += 1;
            inds = inds - length_list;
          }
          id = id_list[element_nr];
        }
        else{
          while(selectedNode != id_list[element_nr]){
            element_nr += 1;
          }          
        }
        setInterval(myFunction,10);
        function myFunction() {
          if(update == 'True'){
            console.log(update);
            element_nr = 0;
            while(selectedNode != id_list[element_nr]){
            element_nr += 1;
            } 
            highlightRow.top = element_nr+1;
            highlightRow.bottom = element_nr;
            highlightRow.fill_alpha = 0.1;
            highlightColumn.right = element_nr+1;
            highlightColumn.left = element_nr;
            highlightColumn.fill_alpha = 0.1;;
            update = 'False';
          }
        }
        highlightRow.top = element_nr+1;
        highlightRow.bottom = element_nr;
        highlightRow.fill_alpha = 0.1;
        highlightColumn.right = element_nr+1;
        highlightColumn.left = element_nr;
        highlightColumn.fill_alpha = 0.1;
        
        set_id_heatmap(id);
        neighbourhoodHighlight();
        source.change.emit();
    """
    )
 

    source.selected.js_on_change("indices", callback_highlight)
    #test_button = Button(label='test', button_type='success')
    #test_button.js_on_click(callback_highlight)
    #print(source.data)
    layout = column(column([type_button, heatmap_figure]), sizing_mode="scale_both")
    
    item_text = json.dumps(json_item(layout, "myplot"))
    file = open(os.path.join(os.path.abspath('flaskr'), 'static\layout.js'), 'w')
    file.write(item_text)
    file.close()
    
    script, div = components(layout)

                
    #File input
    df_csv = df.copy()
    df_csv['year'] = pd.DatetimeIndex(df_csv['date']).year                                                      #Extracts only the year from the date

    #Dataframe filters and groupings
    df_filter = df_csv[['fromJobtitle', 'toJobtitle', 'year', 'sentiment']]                                                  #Extracts these 3 columns
    df_filter['year'] = df_filter['year'].astype(str)                                                           #Sets 'year' as String
    df_filter = df_filter.groupby(df_filter.columns.tolist(),as_index=False).size()                             #Count how many emails sent
    print(df_filter.columns.tolist())
    df_final = df_filter.groupby(['fromJobtitle', 'year'], as_index = False).sum()            

    df_final['x'] = df_final[['fromJobtitle', 'year']].apply(lambda x: (x[0],str(x[1])), axis=1)                 #Group data by year and job title
    df_label = df_filter.groupby(['year'], as_index = False).sum() 
    

    #Create color map for sentiment
    sentiment_mapper = linear_cmap(field_name='sentiment', palette=Viridis256 ,low=df_final['sentiment'].min() ,high=df_final['sentiment'].max())
    
    #create colorbar
    sentiment_colorbar = ColorBar(color_mapper=sentiment_mapper['transform'], label_standoff=12)
    #Plot the bar graph

    TOOLTIPS = [
        ("Function and year", "@x"),
        ("Number of people with this job", "@size"),
    ]
    
    


    LABELS = df_label['year'].unique().tolist()
    #active labels
    active_LABELS=[]
    i=0
    while i < len(LABELS):
        active_LABELS.append(i)
        i += 1


    checkbox_group = CheckboxButtonGroup(labels=LABELS, active=active_LABELS)

    
    

    source = ColumnDataSource(df_final)
    all_source = ColumnDataSource(df_final)

    p = figure(
        x_range=FactorRange(*(df_final["x"])),
        width=1400,
        tooltips= TOOLTIPS,
        title="Emails sent by each jobtitle each year",
        tools = 'hover,save,pan,box_zoom,reset,wheel_zoom'
    )


    p.vbar(
        x="x",
        top="size",
        width=0.9,
        source=source,
        fill_color=sentiment_mapper
    )

    bar_callback = CustomJS(args=dict(source=source, all_source=all_source, labels=LABELS), code="""
        var all_data = all_source.data;
        var old_data = source.data;
        var labels = labels;
        var active = this.active;
        var drop = [];
        var i;
        var j;
        var k;
        var list_drop = [];
        var jsonDrop =[];
        let dropIndices;
        var nonDrop = [];
        var lengthArray = [];

        old_data['year'] = [... all_data['year']];
        old_data['sentiment'] = [... all_data['sentiment']];
        old_data['fromJobtitle'] = [... all_data['fromJobtitle']];
        old_data['x'] = [... all_data['x']];
        old_data['index'] = [... all_data['index']];
        old_data['size'] = [... all_data['size']];

        for(i=0; i < labels.length; i++){  
            if(active.indexOf(i) == -1){
                drop.push(i);
            }
            lengthArray.push(i);
        }    
        for(i=0; i < drop.length; i++){
            list_drop.push(labels[drop[i]]);
        }
        
        for(j=0; j < list_drop.length; j++){
            for(i=0; i < old_data.year.length; i++){
                if(old_data.year.indexOf(list_drop[j], i) != -1){
                    jsonDrop.push(old_data.year.indexOf(list_drop[j], i));
                }
            }
        }

        dropIndices = [...new Set(jsonDrop)];
        dropIndices.sort(function(a,b){
            return a-b;
        });

        for(i=0; i < lengthArray.length; i++){
            for(j=0; j < drop.length; j++){
                if(lengthArray[i] == drop[j]){
                    nonDrop.push(lengthArray.splice(drop[i], 1));
                }
            }
        }

        var tempSent = Array.from(old_data['sentiment']);
        
        

        for(i=0; i < dropIndices.length; i++){
            old_data['year'].splice(dropIndices[i] - i,1);
            old_data['fromJobtitle'].splice(dropIndices[i]- i, 1);
            old_data['size'].splice(dropIndices[i]- i, 1);
            old_data['x'].splice(dropIndices[i]- i, 1);
            old_data['index'].splice(dropIndices[i]- i, 1);
            tempSent.splice(dropIndices[i]- i, 1);
        }

        var tempSent64 = new Float64Array(tempSent);
        old_data['sentiment'] = [... tempSent64];

        console.log(labels);
        console.log(all_data);
        console.log(this.active);
        console.log(drop);
        console.log(list_drop);
        console.log(dropIndices);
        console.log(old_data);
        source.change.emit();
        """)
                
    checkbox_group.js_on_click(bar_callback)
                


    #add colorbar to p
    p.add_layout(sentiment_colorbar, 'right')

    layout_bar = column(column([checkbox_group, p], sizing_mode = 'scale_width'),sizing_mode = 'scale_both')
        
    script2, div2 = components(layout_bar)
    return render_template("DataBothGraphs.html", div=div,script=script, div2=div2,script2=script2)
