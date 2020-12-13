import urllib.request
import json
import random
import numpy as np
import cv2
from sklearn.cluster import KMeans
import math
import spacy
import settings


def _get_artists(obj):
    artists = ''
    for item in obj['participants']:
            a = []
            if item['role_name'] != 'Donor':
                a.append(item['person_name'])
            if len(a) > 1:
                artists = ', '.join(a)
            if len(a) == 1:
                artists = a[0]
    return artists


def _frequencies(labels):
    (hist,_) = np.histogram(labels, bins=5)
    hist = hist.astype(float)
    hist /= hist.sum()
    hist = hist[(-hist).argsort()].astype(str)
    return list(hist)


def _distances(top,test):
    dist_r = (top[0] - int(test[0]))**2
    dist_g = (top[1] - int(test[1]))**2
    dist_b = (top[2] - int(test[2]))**2
    distance = (dist_r + dist_g + dist_b)**0.5
    return distance
            

def _nearest_color(top_colors):
    colors_file = open('./static/colors.txt', 'r')
    colors_contents = colors_file.read().split('\n')
    name_color = [item.split(' '*3) for item in colors_contents]
    color_list = [item[len(item)-1].split(',') for item in name_color]
    name_color = [item[0] for item in name_color]
    nearest_colors = []
    for color in top_colors:
        nearest_color = 0
        for i in range(len(color_list)):
            a = _distances(color, color_list[nearest_color])
            b = _distances(color, color_list[i])
            if a > b:
                nearest_color = i
        nearest_colors.append(name_color[nearest_color])
    colors_file.close()
    return nearest_colors


def _describe_desc(desc):
    nlp = spacy.load('en_core_web_sm')
    string = ' '.join(desc)
    string = string.split()
    described = {}
    for s in string:
        token = nlp(s)
        for t in token:
            if t.text.isalpha() and len(t.text) > 1:  # 1 chars not necessary
                kind = t.head.pos_
                if kind not in described.keys():
                    described[kind] = [t.text.lower()]
                if kind in described.keys():
                    if t.text not in described[kind]:
                        described[kind] += [t.text.lower()]
    return described


def _get_word(diction):
    if len(diction) > 0:
        random.shuffle(diction)
        string = diction[random.randint(0,len(diction)-1)]
        diction.remove(string) # so to not reuse
        string += ' ' * random.randint(0,12)
        return string
    else:
        return ' ' * 2 # add spaces, for form 


def _get_pos(diction):
    kinds = ['PROPN', 'NOUN', 'ADJ', 'ADV', 'ADP', 'VERB', 'DET'] # plan to use
    buckets = [[] for _ in range(len(kinds))]
    for k in kinds:
        if k in diction.keys():
            if k == 'PROPN':
                buckets[0]+= diction['PROPN']
            elif k == 'NOUN':
                buckets[0] +=  diction['NOUN']
            elif k == 'ADJ':
                buckets[1] += diction['ADJ']
            elif k == 'ADP':
                buckets[2] += diction['ADP']
            elif k == 'ADV':
                buckets[2] += diction['ADV']
            elif k == 'VERB':
                buckets[3] += diction['VERB']
            elif k == 'DET':
                buckets[4] += diction['DET']
    return buckets


def _create_poem(diction):
    diction = _get_pos(diction)
    nouns, adjs, ads, verbs, det = diction[0],diction[1],diction[2],diction[3],diction[4]
    poem = ''
    lines = random.randint(5,8)
    previous = 0
    draws = list(range(0,6))
    for i in range(lines):
        draw = random.choice(draws)
        previous = draw
        if draw == 0:
            line = [_get_word(random.choice([det, adjs, verbs, nouns, ads])), '\n']
        elif draw == 1:
            line = [_get_word(adjs), _get_word(nouns), '\n']
        elif draw == 2:
            line = [_get_word(adjs), _get_word(nouns), '\n']
        elif draw == 3:
            word = _get_word(random.choice([verbs, adjs]))
            word *= random.randint(1,3)
            line = [word, '\n']
        elif draw == 4:
            line = [_get_word(random.choice([verbs, adjs, nouns])), '\n']
        else:
            line = [_get_word(random.choice([adjs, ads, nouns])), _get_word(random.choice([adjs, nouns])), _get_word(nouns), '\n']
        poem += ' '.join(line)
        draws = list(range(0,6))
        draws.pop(previous)
    print('\n' + '+'*5 + ' poem made by your computer <3 ' + '+'*5 + '\n\n' + poem + '\n' + '+'*30 + '\n')
    return poem


def _get_top_colors(data):
    urllib.request.urlretrieve(data['img'],'./data/0.jpg') # download image, dummy file
    img = cv2.imread('./data/0.jpg') # img pixels
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # convert bgr to rgb
    modified_img = img.reshape(img.shape[0]*img.shape[1],3) # convert 3d list to 2d
    kmeans = KMeans(n_clusters=5) # use kmeans algorithm to find 5 clusters of colors
    labels = kmeans.fit_predict(modified_img)
    center_colors = kmeans.cluster_centers_
    top_colors = center_colors.astype(int)
    top_colors_str = []
    for colors in top_colors:
        for c in colors:
            top_colors_str.append(str(c))
    data['top_colors'] = top_colors_str
    data['frequencies'] = _frequencies(labels)
    data['desc'].extend(_nearest_color(top_colors))
    diction = _describe_desc(data['desc']) # describing words with spacy
    data['poem'] = _create_poem(diction)
    return data


def get_image():
    rand_page = str(random.randint(1,2))
    url = 'https://api.collection.cooperhewitt.org/rest/?method=cooperhewitt.objects.tags.getObjects&access_token=' + settings.ACCESS_TOKEN + '&has_images=1&tag_id=68797165&page=' + rand_page + '&per_page=257'
    response = urllib.request.urlopen(url).read().decode('utf-8')
    data = json.loads(response) # load json
    objects = data["objects"]
    choices = list(range(0,len(objects)-1))
    flag, i = False, 0
    while not flag and i < len(choices):
        rand_ind = random.choice(choices)
        obj = objects[rand_ind]
        desc = obj['description']
        try:
            if desc is not None: # only want images with descriptions
                image_data = {'name': obj['title'], 'artist': _get_artists(obj), 'url': obj['url'],
                            'img': obj['images'][0]['b']['url'], 'desc': [desc]}
                image_data = _get_top_colors(image_data)
                flag = True
        except:
            continue
        choices.remove(rand_ind)
        i+=1
    return image_data
    

if __name__ == '__main__':
    print(get_image())
    
    