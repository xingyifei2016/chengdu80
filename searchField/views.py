import re
from django.shortcuts import render
from django.utils.http import urlunquote, urlquote
from django.contrib import messages
from django.http import Http404
from django.core.cache import cache
import os
from django.conf import settings
from time import time
from . import topics
from operator import itemgetter
import numpy as np
import string
import random
import sys
import pickle


STOP_WORDS_FILENAME = './static/footer/stop_words_topic.txt'
data_location = "./static/footer/topic_data.txt"
fields_base = "./static/footer/fields.pkl"
repository = topics.BookInventory(data_location, STOP_WORDS_FILENAME)
repository.load_books()
docs_number = repository.books_count()
all_fields = ['fieldName', 'subfieldName']
searched_query = {i: [] for i in all_fields}
searched_query["results"] = {}
default_fields = ['Fintech', 'Economics', 'Statistics']
with open(fields_base, 'rb') as f:
    data = pickle.load(f)



def details(request):
    #Request is only person, find all relevant details about this person
    timeTaken = time()
    field = request.GET['field']
    subfield = request.GET['subfield']
    # assert False, data

    ids = request.GET['id']
    results = data[ids]

    
    # temp_results = [{'coauthors': np.random.rand(), 'field': np.random.rand(), 'title': ''.join(random.choice(string.ascii_lowercase) for x in range(5))} for i in range(10)]
    image_url1 = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1572436502562&di=5a296d58b1c1ca0cbd21c9fedde519fd&imgtype=0&src=http%3A%2F%2Fi0.hdslb.com%2Fbfs%2Farticle%2Ffd1515ed28998c886a1c48acf7454f15a83b5b1b.jpg"
    image_url2 = "/static/footer/DaronAcemoglu.png"
    
    end_time = time()
    timeTaken = int(end_time - timeTaken)
    context = {
        'imageurl1': image_url1,
        'imageurl2': image_url2,
        'timeTaken': timeTaken,
        'field': field,
        'subfield': subfield,
        'ranking': results,
        }
    return render(request, 'detailsFields.html', context)

def search(request):
    timeTaken = time()
    if request.method != 'POST':
        if len(searched_query['fieldName']) == 0:
            fields = default_fields
        else:
            fields = sorted(searched_query['results'].keys(), key=lambda x: searched_query['results'][x], reverse=True)[:5]
        context = {
            'fields': fields,
        }

        return render(request, 'searchFields.html', context)
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    available_info = [i for i in all_fields if request.POST[i] is not '']

    if len(available_info) != 0:
        query = ' '.join([str(request.POST[i]) for i in available_info])
        result = repository.search_books(query)
        #Hard code raw inputs expecting all queries selected
        image_url1 = "/static/footer/network.png"
        image_url2 = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1572343490091&di=97c216a924ed1603a5723045557f3e37&imgtype=0&src=http%3A%2F%2Fimg.pconline.com.cn%2Fimages%2Fupload%2Fupc%2Ftx%2Fsoftbbs%2F1011%2F06%2Fc0%2F5768221_1289012169875_1024x1024.png"
        fieldName = urlunquote(request.POST['fieldName'])
        subfieldName = urlunquote(request.POST['subfieldName'])
        
        end_time = time()
        timeTaken = int(end_time - timeTaken)
        if type(result)==str:
            messages.error(request, 
                'Error: No fields matched')
            if len(searched_query['fieldName']) == 0:
                fields = default_researchers
            else:
                fields = sorted(searched_query['results'].keys(), key=lambda x: searched_query['results'][x], reverse=True)[:5]
            context = {
                'fields': fields,
            }
            return render(request, 'searchFields.html', context)

        for i in available_info:
            searched_query[i].append(str(request.POST[i]))

        for j in result:
            if j['field'] in searched_query['results']:
                searched_query['results'][j['field']] += j['score']
            else:
                searched_query['results'][j['field']] = j['score']
        print(result)
        temp_results = result
        context = {
        'imageurl1': image_url1,
        'imageurl2': image_url2,
        'fieldName': fieldName,
        'subfieldName': subfieldName,
        'timeTaken': timeTaken,
        'ranking': temp_results,
        'num_visits': num_visits,
        }

        return render(request, 'resultsFields.html', context)
    else:
        messages.error(request, 'Error: no queries')
        return render(request, 'searchFields.html')


    
    