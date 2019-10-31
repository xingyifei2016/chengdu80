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

STOP_WORDS_FILENAME = '/Users/yifeixing/desktop/chengdu80/static/footer/stop_words.txt'
data_location = "/Users/yifeixing/desktop/chengdu80/static/footer/data.txt"
repository = searcher.BookInventory(data_location, STOP_WORDS_FILENAME)
repository.load_books()
docs_number = repository.books_count()
all_fields = ['researchName', 'paperName', 'affiliation', 'field', 'journal']
searched_query = {i: [] for i in all_fields}
searched_query["results"] = {}
default_researchers = ['John Denero', 'Jay Keasling', 'Stella Yu']


def details(request):
    #Request is only person, find all relevant details about this person
    timeTaken = time()
    temp_results = [{'coauthors': np.random.rand(), 'field': np.random.rand(), 'title': ''.join(random.choice(string.ascii_lowercase) for x in range(5))} for i in range(10)]
    image_url1 = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1572436502562&di=5a296d58b1c1ca0cbd21c9fedde519fd&imgtype=0&src=http%3A%2F%2Fi0.hdslb.com%2Fbfs%2Farticle%2Ffd1515ed28998c886a1c48acf7454f15a83b5b1b.jpg"
    image_url2 = "/static/footer/DaronAcemoglu.png"
    field = "Some field"
    journal = "Some journal"
    affiliation = "Some affiliation"
    paperName = "Some paper"
    researchName = "Some Name"
    end_time = time()
    timeTaken = int(end_time - timeTaken)
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
        }

        return render(request, 'results.html', context)
    else:
        messages.error(request, 'Error: no queries')
        return render(request, 'search.html')


    
    