#IMPORT NECESSARY LIBRARIES

import os
import pandas as pd
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

import urllib

from datetime import datetime

#FLASK SETUP               
app = Flask(__name__)


# Reading Data from the csv file which is the minmal sample set from the dataset
youtubeVids = pd.read_csv('./data.csv')

# RENAME COLUMNS
youtubeVids = youtubeVids.rename(columns={'country': 'country', 'video_id': 'video_id', 
'title': 'title', 'publishedAt': 'publishedAt', 'channelTitle': 'channelTitle', 
'categoryId': 'categoryId','trending_date': 'trending_date',
'view_count': 'views', 'likes': 'likes', 'dislikes': 'dislikes', 
'comment_count': 'comments', 'thumbnail_link': 'thumbnail_link'})


# HOME ROUTE
@app.route("/")
def home():
    return render_template("index.html")

##############ROUTES FOR DROP DOWN MENU############

# ROUTE FOR DROP DOWN MENU 1

@app.route("/dropdown1")
def dropdown1():
    country_df = youtubeVids['country'].value_counts()
    countryList = country_df.index.tolist()
    return jsonify(countryList)

# ROUTE FOR DROP DOWN MENU 2
@app.route("/dropdown2")
def dropdown2():
    category_df = youtubeVids['categoryId'].value_counts()
    categoryList = category_df.index.tolist()
    return jsonify(categoryList)

# ROUTE FOR DROP DOWN MENU 3
@app.route("/dropdown3")
def dropdown3():
    metricList = ['views', 'likes', 'dislikes', 'comments']
    return jsonify(metricList)


# ROUTES FOR DATA

####################### ROUTE FOR BAR GRAPH 1 ##########################

@app.route("/dataset1/<country>/<metric>")
def dataset1(country, metric):
    # Sort dataframe by country & category & metric
    barGraph1Data = youtubeVids[youtubeVids["country"] == country]
    barGraph1Data = barGraph1Data.groupby('categoryId').mean()
    barGraph1Data = barGraph1Data[metric]

    ##### Convert data to a dictionary #####
    barGraph1Data = barGraph1Data.to_dict()

    ##### Jsonify the data #####
    return jsonify(barGraph1Data)

####################### ROUTE FOR BAR GRAPH 2 ##########################
@app.route("/dataset2/<country>/<category>/<metric>")
def dataset2(country=None, category=None, metric=None):
    # Sort dataframe by country & category & select columns to keep
    barGraph2Data = youtubeVids[youtubeVids["country"] == country]
    barGraph2Data = barGraph2Data[barGraph2Data["categoryId"] == category]
    barGraph2Data = barGraph2Data.loc[:, ["views", "comments", "likes", 
                                            "dislikes", "country", "categoryId"]]

    # Create a table (df) of metric values vs the count of each value for bargraph
    metric_values = ["views", "comments", "likes", "dislikes"]
    metricMaxValues = []
    n = 0
    for metric in metric_values:
        step1_df = barGraph2Data.sort_values(by=metric, ascending=False)
        step2_df = step1_df[metric]
        step3 = step2_df.values.tolist()
        metricMaxValues.append(step3[0])

    # Create the actual table (df)
    barGraph2_df = pd.DataFrame(
        {'Metric_Values': metric_values,
         'Max_Value': metricMaxValues
         })

    ##### Convert data to a dictionary #####
    barGraph2_df = barGraph2_df.to_dict()

    ##### Jsonify the data #####
    return jsonify(barGraph2_df)

####################### ROUTE FOR LINE GRAPH ##########################
@app.route("/dataset3/<country>/<metric>")
def dataset3(country, metric):
    lineData = youtubeVids[youtubeVids["country"] == country]

    # add a timestamp column to dataframe
    timestamps = []
    for index, row in lineData.iterrows():
        t = row["publishedAt"]
        format_str = '%Y-%m-%d' # The format
        tt = datetime.strptime(t, format_str)
        td = datetime(tt.year, tt.month, tt.day)
        datetime.timestamp(td)
        timestamps.append(datetime.timestamp(td))
    lineData["timestamp"] = timestamps

    # get top three categories
    topThree = list(lineData.groupby(["categoryId"]).sum()[
                    "likes"].sort_values(ascending=False).index[0:3])

    # Select one category and group by timeStamp
    first = lineData[lineData["categoryId"] == topThree[0]]
    first = first.groupby("timestamp").sum()

    ##### Convert data to a dictionary #####
    first = first[metric].to_dict()
    ##### Jsonify the data #####
    return jsonify(first)

####################### ROUTE FOR TOP 10 TABLE ##########################
@app.route("/dataset4/<country>/<category>/<metric>")
def dataset4(country=None, category=None, metric=None):
    # Sort dataframe by country & category
    table_df = youtubeVids[youtubeVids["country"] == country]
    table_df = table_df[table_df["categoryId"] == category]

    # print('metric=', metric)
    # Sort dataframe (largest to smallest) by metric selected
    sorted_table_df = table_df.sort_values(by=metric, ascending=False)

    # Remove duplicate videos from dataframe
    sorted_table_df = sorted_table_df.drop_duplicates(subset='title', keep="first")

    # Select top 10 (based on metric selected) from dataframe
    top10TableData_df = sorted_table_df.nlargest(10, metric)

    # Select columns to keep for table
    top10TableData_df = top10TableData_df[['categoryId', 'country', 'title', 'channelTitle',
                                           'views', 'comments', 'trending_date', 
                                           'likes', 'dislikes', 'video_id', 'thumbnail_link']]

    ##### Convert data to a dictionary #####
    top10TableData = top10TableData_df.to_dict(orient="records")

    ##### Jsonify the data #####
    return jsonify(top10TableData)

######################### ROUTE FOR ALL DATA ############################
@app.route("/allData")
def allData():
    allData = youtubeVids

    allData = allData.to_dict()

    return jsonify(allData)

# CLOSE IF LOOP

if __name__ == "__main__":
    app.run(debug=True)

# END OF FLASK APP           
