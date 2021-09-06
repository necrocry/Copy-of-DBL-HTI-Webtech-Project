##Author: Josericho M Rachmat, 2021
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

from flask import Blueprint 

from flask import render_template
import os

bargraph = Blueprint('Bargraph', __name__)

@bargraph.route('/bargraph_code')

def bargraph_code():
            
            #File input path
            csv_path = os.path.join(os.path.abspath('flaskr'), 'static\csvs\csv_file.csv')
            df_csv = pd.read_csv(csv_path)
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

            layout = column(checkbox_group, p)
                
            script, div = components(layout)
            return render_template('bar_graph.html',div=div, script=script)  
