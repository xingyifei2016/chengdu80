import re
from django.shortcuts import render
from django.utils.http import urlunquote, urlquote
from django.contrib import messages
from django.http import Http404
from django.core.cache import cache
import os
from django.conf import settings
from time import time
from . import searcher
from operator import itemgetter
import numpy as np
import string
import random
import pandas as pd
from django.http import HttpResponseRedirect


STOP_WORDS_FILENAME = './static/footer/stop_words.txt'
data_location = "./static/footer/data.txt"
repository = searcher.BookInventory(data_location, STOP_WORDS_FILENAME)
repository.load_books()
docs_number = repository.books_count()
all_fields = ['researchName', 'paperName', 'affiliation', 'field', 'journal']
searched_query = {i: [] for i in all_fields}
searched_query["results"] = {}
default_researchers = ['John Denero', 'Jay Keasling', 'Stella Yu']
df = pd.read_csv('./static/footer/nodup_joined.csv')
sample = [["Jacob Kean", "Law and Economics~Regulation and Business Law", "#8DD3C7"], ["Jamie Reilly", "Mathematical and Quantitative Methods~Econometric and Statistical Methods:  Special Topic", "#FFFFB3"], ["Jonathan Peelle", "Mathematical and Quantitative Methods~Game Theory and Bargaining Theor", "#BEBADA"]]

def details(request):
    #Request is only person, find all relevant details about this person
    timeTaken = time()
    authorID = request.GET['authorID']

    query = df.loc[df['author_id'] == np.float64(authorID)]
    if len(query) == 0:
        messages.error(request, 'Error: No researchers matched from database')
        if len(searched_query['researchName']) == 0:
            researchers = default_researchers
        else:
            researchers = sorted(searched_query['results'].keys(), key=lambda x: searched_query['results'][x], reverse=True)[:5]
        context = {
            'researchers': researchers,
        }
        return HttpResponseRedirect('/search/')

    # temp_results = [{'coauthors': np.random.rand(), 'field': np.random.rand(), 'title': ''.join(random.choice(string.ascii_lowercase) for x in range(5))} for i in range(10)]
    image_url1 = query['URL'].values[0]
    image_url2 = "/static/footer/DaronAcemoglu.png"
    weighted_degree = query['Weighted.Degree'].values[0]
    pagerank = query['pageranks'].values[0]
    clustering = query['clustering'].values[0]
    eigencentrality = query['eigencentrality'].values[0]
    name = query['name'].values[0]
    end_time = time()
    timeTaken = int(end_time - timeTaken)
    context = {
        'imageurl1': image_url1,
        'imageurl2': image_url2,
        'weighted_degree': weighted_degree,
        'page': pagerank,
        'timeTaken': timeTaken,
        'cluster': clustering,
        'eigen': eigencentrality,
        'name': name,
        }
    return render(request, 'details.html', context)

def search(request):
    timeTaken = time()
    if request.method != 'POST':
        if len(searched_query['researchName']) == 0:
            researchers = default_researchers
        else:
            researchers = sorted(searched_query['results'].keys(), key=lambda x: searched_query['results'][x], reverse=True)[:5]
        context = {
            'researchers': researchers,
        }
        return render(request, 'search.html', context)
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    available_info = [i for i in all_fields if request.POST[i] is not '']

    if len(available_info) != 0:
        query = ' '.join([str(request.POST[i]) for i in available_info])
        result = repository.search_books(query)
        #Hard code raw inputs expecting all queries selected
        image_url1 = "/static/footer/network.png"
        image_url2 = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1572343490091&di=97c216a924ed1603a5723045557f3e37&imgtype=0&src=http%3A%2F%2Fimg.pconline.com.cn%2Fimages%2Fupload%2Fupc%2Ftx%2Fsoftbbs%2F1011%2F06%2Fc0%2F5768221_1289012169875_1024x1024.png"
        researchName = urlunquote(request.POST['researchName'])
        field = urlunquote(request.POST['field'])
        journal = urlunquote(request.POST['journal'])
        affiliation = urlunquote(request.POST['affiliation'])
        paperName = urlunquote(request.POST['paperName'])
        end_time = time()
        timeTaken = int(end_time - timeTaken)
        if type(result)==str:
            messages.error(request, 
                'Error: No researchers matched')
            if len(searched_query['researchName']) == 0:
                researchers = default_researchers
            else:
                researchers = sorted(searched_query['results'].keys(), key=lambda x: searched_query['results'][x], reverse=True)[:5]
            context = {
                'researchers': researchers,
            }
            return render(request, 'search.html', context)

        for i in available_info:
            searched_query[i].append(str(request.POST[i]))

        for j in result:
            j['expertise'] = j['expertise'].replace(";", ' ')
            if j['professor'] in searched_query['results']:
                searched_query['results'][j['professor']] += j['score']
            else:
                searched_query['results'][j['professor']] = j['score']
        print(searched_query['results'])
        temp_results = result
        context = {
        'imageurl1': image_url1,
        'imageurl2': image_url2,
        'researchName': researchName,
        'paperName': paperName,
        'timeTaken': timeTaken,
        'field': field,
        'affiliation': affiliation,
        'journal': journal,
        'ranking': temp_results,
        'num_visits': num_visits,
        'legend': sample
        }

        return render(request, 'results.html', context)
    else:
        messages.error(request, 'Error: no queries')
        return render(request, 'search.html')


    
    