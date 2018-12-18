# -*- coding: utf-8 -*-
from flask import Flask, redirect, url_for, request, current_app
import string 
from string import digits
import json
import csv
import numpy as np
import sys
import random
from scipy.stats import pearsonr

app = Flask(__name__)

with open('ratings_small.txt') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    result = {}
    input = list(csv_reader)
    count = 0
    for row in input:
        if count == 0:
            count += 1 
            continue
        key = int(row[0])
        if key not in result:
            result[key] = np.zeros((200000,))
        result[key][int(row[1])] = float(row[2])
    app.data = result

movie_name_list = [0]*200000

with open('movies.csv', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    input = list(csv_reader)
    count = 0
    for row in input:
        if count == 0:
            count += 1 
            continue
        movie_id = int(row[0])

        if movie_id not in result:
            movie_name_list[movie_id] = row[1]

movie_imdb_list = [0]*200000

with open('links.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    input = list(csv_reader)
    count = 0
    for row in input:
        if count == 0:
            count += 1 
            continue
        movie_id = int(row[0])

        if movie_id not in result:
            movie_imdb_list[movie_id] = row[1]

@app.route('/')
def index():
   return 'Hello World'

@app.route('/register',methods = ['POST'])
def register():
    if request.method == 'POST':
        chat_id = int(request.form['chat_id'])
        if chat_id in current_app.data:
            return json.dumps({"exists": 1})
        else:
            current_app.data[chat_id] =  np.zeros((200000,))
            return json.dumps({"exists": 0})

@app.route('/get_unrated_movie', methods = ['POST'])
def get_unrated_movie():
    if request.method == 'POST':
        chat_id = int(request.form['chat_id'])
    
    # zero user rating
    user_rating = np.where(np.array(app.data[chat_id]) == 0)[0]
    #non zero movie name
    movie_id_nonzero = np.where(np.array(movie_name_list) != '0')[0]
    #all movie that are not rated
    unrated = np.intersect1d(user_rating,movie_id_nonzero)
    #pick one
    movie_id = np.random.choice(unrated, 1)[0]

    #movie id to imdb id
    imdb_id = movie_imdb_list[movie_id]
    url = "https://www.imdb.com/title/tt{}".format(imdb_id)
    return json.dumps({"id": str(movie_id), "title":str(movie_name_list[movie_id]), "url":url})

@app.route('/rate_movie', methods = ['POST'])
def rate_movie():
    if request.method == 'POST':
        chat_id = int(request.form['chat_id'])
        movie_id = int(request.form['movie_id'])
        rating = float(request.form['rating'])

    current_app.data[chat_id][movie_id] = rating
    return json.dumps({"status": "success"})

@app.route('/recommend', methods = ['POST'])
def recommend():
    #non zero user rating
    if request.method == 'POST':
        chat_id = int(request.form['chat_id'])
        top_n = int(request.form['top_n'])

    user_rating = np.where(np.array(app.data[chat_id]) != 0)[0]
    print(user_rating)
    if len(user_rating) < 10:
        return json.dumps({"chat_id": str(chat_id), "results":[]})
    else:
        temp_dict = {}
        temp = 0
        id = 0
        for i in current_app.data:
            if i != 1:
                r,_ = pearsonr(current_app.data[chat_id], current_app.data[i])
        
                if r > temp:
                    temp = r
                    id = int(i)

        r_mean_user = np.mean([r for r in current_app.data[chat_id] if r > 0])
        r_mean_other = np.mean([r for r in current_app.data[id] if r > 0])
        sim_other_user,_ = pearsonr(app.data[1], current_app.data[id])

        #non zero user rating
        user_rating = np.where(np.array(current_app.data[id]) != 0)[0]
        print(user_rating)

        for i in user_rating:
            pred = r_mean_user + (sim_other_user * (float(current_app.data[id][i]) - r_mean_other))
            temp_dict[pred] = i
        
        temp_list = sorted(temp_dict.items(), key=lambda k: k[1], reverse=True)[:top_n]
        
        result_dict = {}
        result_dict["movies"] = []

        for (pred, i) in temp_list:
            imdb_id = movie_imdb_list[i]
            url = "https://www.imdb.com/title/tt{}".format(imdb_id)
            movie_title = str(movie_name_list[i])
            print(url, movie_title)
            
            temp_dict = {}
            temp_dict["title"] = movie_title
            temp_dict["url"] = url

            result_dict["movies"].append(temp_dict)
        return json.dumps({"chat_id": str(chat_id), "results":result_dict})

if __name__ == '__main__':
   app.run(host='0.0.0.0')