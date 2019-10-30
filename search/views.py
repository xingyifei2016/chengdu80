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


import numpy as np
import string
import random

def details(request):
    #Request is only person, find all relevant details about this person
    timeTaken = time()
    temp_results = [{'coauthors': np.random.rand(), 'field': np.random.rand(), 'title': ''.join(random.choice(string.ascii_lowercase) for x in range(5))} for i in range(10)]
    image_url1 = "https://www.freetechbooks.com/uploads/1463732393-denero.jpg"
    image_url2 = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1572343490091&di=97c216a924ed1603a5723045557f3e37&imgtype=0&src=http%3A%2F%2Fimg.pconline.com.cn%2Fimages%2Fupload%2Fupc%2Ftx%2Fsoftbbs%2F1011%2F06%2Fc0%2F5768221_1289012169875_1024x1024.png"
    researchName = "Some name"
    field = "Some field"
    journal = "Some journal"
    affiliation = "Some affiliation"
    paperName = "Some paper"
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
        return render(request, 'search.html')
    
    all_fields = ['researchName', 'paperName', 'affiliation', 'field', 'journal']
    available_info = [i for i in all_fields if request.POST[i] is not '']

    if len(available_info) != 0:
        #Hard code raw inputs expecting all queries selected
        image_url1 = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1572361994747&di=8c3eeaac622e299c06d45a42ddd4f0fb&imgtype=jpg&src=http%3A%2F%2Fimg3.imgtn.bdimg.com%2Fit%2Fu%3D1490494773%2C3066344520%26fm%3D214%26gp%3D0.jpg"
        image_url2 = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1572343490091&di=97c216a924ed1603a5723045557f3e37&imgtype=0&src=http%3A%2F%2Fimg.pconline.com.cn%2Fimages%2Fupload%2Fupc%2Ftx%2Fsoftbbs%2F1011%2F06%2Fc0%2F5768221_1289012169875_1024x1024.png"
        researchName = urlunquote(request.POST['researchName'])
        field = urlunquote(request.POST['field'])
        journal = urlunquote(request.POST['journal'])
        affiliation = urlunquote(request.POST['affiliation'])
        paperName = urlunquote(request.POST['paperName'])
        end_time = time()
        timeTaken = int(end_time - timeTaken)


        # data = "/Users/yifeixing/desktop/min_title_author.tab.txt"
        # result = searcher.execute_search(data, "one two")
        # result = result.split("\n")
        # new_result = []



        temp_results = [{'score0': np.random.rand(), 'score1': np.random.rand(), 'title': ''.join(random.choice(string.ascii_lowercase) for x in range(5))} for i in range(30)]

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

        return render(request, 'results.html', context)
    else:
        messages.error(request, 'Error: no queries')
        return render(request, 'search.html')


    
    