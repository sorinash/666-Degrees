from flask import Flask, render_template, request
import pickle
#import numpy as np
#import pandas as pd
import networkx as nx
from collections import defaultdict
import os
#from networkx.algorithms import approximation


# To do:
# 1. Use inputs as autofilling lists.
# 2. Get
# 2. Strip out or replace iffy characters, umlauts, etc.
# 3. Include error-catching for incorrect names.


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def form():
    return render_template('form.html',jej=', \n'.join(os.listdir()))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    with open('band_to_id.pkl', 'rb') as f:
        band_to_id = pickle.load(f)
    first_band = request.form['first_band'].replace('&','&amp;')
    second_band = request.form['second_band'].replace('&','&amp;')

    first_okay = first_band in band_to_id.keys()
    second_okay = second_band in band_to_id.keys()
    return render_template('verify.html',first_band=first_band,second_band=second_band,
                           first_okay=first_okay,second_okay=second_okay)



@app.route('/ambig', methods=['GET', 'POST'])
def ambiguous():
#    with open('band_to_id.pkl', 'rb') as f:
#        band_to_id = pickle.load(f)

    with open('id_to_band.pkl', 'rb') as f:
        id_to_band = pickle.load(f)

    with open('id_to_guy.pkl', 'rb') as f:
        id_to_guy = pickle.load(f)

#    with open('guy_to_id.pkl', 'rb') as f:
#        guy_to_id = pickle.load(f)

    with open('band_members.pkl', 'rb') as f:
        band_members = pickle.load(f)
    print(request.form['first_band'])

    first_bandname = request.form['first_band']
    second_bandname = request.form['second_band']

    new_band_to_id = defaultdict(set)
    for i in id_to_band.keys():
        new_band_to_id[id_to_band[i]].add(i)

    first_bandlist = [i for i in new_band_to_id[first_bandname]]
    second_bandlist = [i for i in new_band_to_id[second_bandname]]

    print([band for band in first_bandlist])

    first_bandmembers = [[id_to_guy[guy] for guy in band_members[band]] for band in first_bandlist]
    second_bandmembers = [[id_to_guy[guy] for guy in band_members[band]] for band in second_bandlist]

    for i in range(len(first_bandmembers)):
        if len(first_bandmembers[i]) > 5:
            first_bandmembers[i] = first_bandmembers[i][0:5]
    for i in range(len(second_bandmembers)):
        if len(second_bandmembers[i]) > 5:
            second_bandmembers[i] = [i for i in second_bandmembers[i][0:5] if i != '']

    first_bandmembers = [', '.join(i) for i in first_bandmembers]
    second_bandmembers = [', '.join(i) for i in second_bandmembers]

    print(first_bandmembers)
    print(second_bandlist)
    return render_template('ambig.html',first_band=request.form['first_band'],second_band=request.form['second_band'],
                           fbl=first_bandlist,sbl=second_bandlist,fbm=first_bandmembers,sbm=second_bandmembers)

@app.route('/disambig', methods=['GET', 'POST'])
def disambig():
    #with open('band_to_id.pkl', 'rb') as f:
    #    band_to_id = pickle.load(f)

    with open('id_to_band.pkl', 'rb') as f:
        id_to_band = pickle.load(f)

    with open('id_to_guy.pkl', 'rb') as f:
        id_to_guy = pickle.load(f)

    #with open('guy_to_id.pkl', 'rb') as f:
    #    guy_to_id = pickle.load(f)

    with open('band_members.pkl', 'rb') as f:
        band_members = pickle.load(f)

   # with open('member_of_bands.pkl', 'rb') as f:
   #     member_of_bands = pickle.load(f)
    with open('new_band_to_id.pkl','rb') as f:
        new_band_to_id = pickle.load(f)
    with open('band_graph.pkl','rb') as f:
        G = pickle.load(f)
    print(request.form['unambig_fb'])
    print(request.form['unambig_sb'])
    def traverse_network(first_id, second_id, G, band_members, id_to_guy, id_to_band, new_band_to_id):
        if nx.has_path(G,first_id,second_id) == False:
            return [False, True, 'These two bands are not connected.']
        path = nx.dijkstra_path(G,first_id,second_id)
        outstr = ''
        outlist =[]
        for i in range(1,len(path)):
            first_band_members = list(band_members[path[i-1]])
            second_band_members = list(band_members[path[i]])
            shared_band_members = [j for j in first_band_members if j in second_band_members]
            if len(shared_band_members) == 1:
                firstpath = id_to_band[path[i-1]].replace('&amp;','&')
                secondpath = id_to_band[path[i]].replace('&amp;','&')
                outstr += f'{i}. {id_to_guy[shared_band_members[0]]} was in both {firstpath} and {secondpath}\n'
                outlist.append(f'{id_to_guy[shared_band_members[0]]} was in both {firstpath} and {secondpath}')
            else:
                shared_band_members = [id_to_guy[jej] for jej in shared_band_members]
                shared_band_members[-1] = 'and ' + shared_band_members[-1]
                use_str = ', '.join(shared_band_members)
                outlist.append(f'{use_str} were in both {id_to_band[path[i-1]]} and {id_to_band[path[i]]}')
        print(outlist)
        return [True, True, outlist,True]
    a=traverse_network(request.form['unambig_fb'],request.form['unambig_sb'],G, band_members, id_to_guy, id_to_band, new_band_to_id)
    fbn = id_to_band[request.form['unambig_fb']].replace('&amp;','&')
    sbn = id_to_band[request.form['unambig_sb']].replace('&amp;','&')
    if a[0] == True:
        return render_template('disambig.html',okay=True,first_band=fbn,second_band=sbn,degrees_sep=a[2])
    else:
        return render_template('disambig.html',okay=False,first_band=sbn,second_band=sbn,degrees_sep=a[2])


if __name__ == "__main__":
    app.run()

