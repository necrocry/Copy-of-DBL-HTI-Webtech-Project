from inspect import Attribute
from bokeh.core.enums import SizingMode
from bokeh.models.tools import Tap
from bokeh.models.widgets.buttons import Toggle
import pandas as pd
import numpy as np
import json


from bokeh.io import show
from bokeh.models import BasicTicker, LinearColorMapper, PrintfTickFormatter, ColumnDataSource, Button, ColorBar, Plot, BoxAnnotation, TapTool
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import column, row
from bokeh.palettes import Greys256
from bokeh.models.callbacks import CustomJS
from bokeh.transform import linear_cmap
from bokeh import events
from bokeh.embed import json_item

from flask import Blueprint
from flask import render_template
import os

heatmap = Blueprint('heatmap', __name__)

@heatmap.route('/heatmap_code')
def heatmap_code():
    #create a dataframe from CSV file
    csv_path = os.path.join(os.path.abspath('flaskr'), 'static\csvs\csv_file')
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
    type_button = Toggle(label='Change CC', button_type='success')
    
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
    
    #callback for highlighting the selected row
    callback_highlight= CustomJS(args=dict(source=source, length_list=length_list, id_list=id_list, heatmap_figure=heatmap_figure, highlightRow=highlightRow, highlightColumn=highlightColumn), code="""
        var highlightRow = highlightRow;
        var highlightColumn = highlightColumn;
        var inds = source.selected.indices
        var element_nr = 0;
        while(inds >= length_list){
            element_nr += 1
            inds = inds - length_list
        }
        highlightRow.top = element_nr+1;
        highlightRow.bottom = element_nr;
        highlightRow.fill_alpha = 0.1;
        highlightColumn.right = element_nr+1;
        highlightColumn.left = element_nr;
        highlightColumn.fill_alpha = 0.1;
        source.change.emit();
    """
    )
    source.selected.js_on_change("indices", callback_highlight)
    #test_button = Button(label='test', button_type='success')
    #test_button.js_on_click(callback_highlight)
    #print(source.data)
    layout = column(type_button, row(heatmap_figure, sizing_mode= 'scale_both'))

    item_text = json.dumps(json_item(layout, "myplot"))
    file = open(os.path.join(os.path.abspath('flaskr'), 'static/layout.js'), 'w')
    file.write(item_text)
    file.close()
    
    script, div = components(layout)
    return render_template('Visualization_page1.html',div=div, script=script)  