import heapq
import os
import random
import re
import requests
import time
import traceback
from pyquery import PyQuery as pq

more_users_depth = 5


sleep_time = 1

headers = {
        'accept-encoding': 'gzip, deflate',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }

remove_year_regex = re.compile(r"\d+ ")

get_percent_regex = re.compile(r"\d+")

movie_url_base = "https://tastedive.com/like/"

url_base = "https://tastedive.com/"

done_profiles = set()

done_movies = set(['Avengers-Endgame'])

queue_profiles = []

queue_movies = []
heapq.heappush(queue_movies, (0,'Avengers-Endgame'))

def scrape_movie():
    key = heapq.heappop(queue_movies)[1]
    response = requests.get(movie_url_base+key, headers=headers)
    root = pq(response.text)
    add_user_names(root)
    for i in range(more_users_depth):
        root = get_more_users(root)
        if root is None:
            break
        add_user_names(root)

def add_user_names(root):
    likes_div = root('.tk-User-link')
    for link in likes_div:
        username = link.attrib['href'][1:]
        if username not in done_profiles:
            done_profiles.add(username)
            heapq.heappush(queue_profiles, (random.random(),username))

def get_more_users(root):
    more_buttons = root('.tk-More')
    if len(more_buttons) == 0:
        return None

    more_button = more_buttons[0]

    more_url = url_base + more_button.attrib['data-endpoint'][1:]

    time.sleep(sleep_time)

    response = requests.get(more_url, headers=headers)

    return pq(response.text)
    
def get_first_or_default(root,query,attrib,default=""):
    element = root(query)
    return element[0].attrib[attrib] if len(element) else default

def get_first_or_empty_text(root,query):
    element = root(query)
    return element[0].text if len(element) else ''

def add_card_rows(root,output_file, user):
    cards = root(".tk-Resource.js-resource-card")
    for card in cards:
        card_root = root(card)
        id = card.attrib['data-resource-info-id']
        title = card.attrib['title'].replace('"','')
        year = card.attrib['data-disambiguation']
        key = card_root('.tk-Resource-labels')[0].attrib['href'][6:]
        if key not in done_movies:
            done_movies.add(key)
            heapq.heappush(queue_movies, (random.random(),key))
        like = '1'
        media_type = remove_year_regex.sub("",get_first_or_empty_text(card_root,'.tk-Resource-type'))
        percent_like = get_percent_regex.search(get_first_or_default(card_root,'.tk-Rating-bar--like','style','0')).group(0)
        percent_dislike = get_percent_regex.search(get_first_or_default(card_root,'.tk-Rating-bar--meh','style','0')).group(0)
        percent_meh = get_percent_regex.search(get_first_or_default(card_root,'.tk-Rating-bar--dislike','style','0')).group(0)
        num_likes = get_first_or_empty_text(card_root,'.js-card-likes-counter')
        image = get_first_or_default(card_root,'.tk-Resource-image','src','')
        array = [user,title,key,id,like,media_type,percent_like,percent_dislike,percent_meh,num_likes,year,image]
        output_file.write("\""+"\",\"".join(array)+"\"")
        output_file.write("\n")

def get_more_titles(root):
    more_buttons = root('.tk-Resources-more')
    if len(more_buttons) == 0:
        return None

    more_button = more_buttons[0]

    more_url = url_base + more_button.attrib['data-endpoint'][1:]

    time.sleep(sleep_time)

    response = requests.get(more_url, headers=headers)

    return pq(response.text)

def scrape_profile(output_file):
    if len(queue_profiles) == 0 or random.random() < 0.01:
        scrape_movie()
        time.sleep(sleep_time)
    try:
        user = heapq.heappop(queue_profiles)[1]
    except:
        print(queue_profiles)
        print(heapq.heappop(queue_profiles))
        return
    response = requests.get(url_base+user, headers=headers)
    root = pq(response.text)
    add_card_rows(root,output_file,user)
    more_buttons = root('.tk-Resources-more')

    flush(output_file)

    for more_button in more_buttons:
        time.sleep(sleep_time)

        more_url = url_base + more_button.attrib['data-endpoint'][1:]

        response = requests.get(more_url, headers=headers)

        more_root = pq(response.text)

        while more_root is not None:
            add_card_rows(more_root,output_file,user)
            more_root = get_more_titles(more_root)

    flush(output_file)

def flush(file):
    file.flush()
    os.fsync(file.fileno())

def main():
    output_file = open("data.csv","a", encoding="utf-8")
    log_file = open("log.txt","w", encoding="utf-8")

    count = 0

    while(True):
        try:
            scrape_profile(output_file)
            count += 1
            print(count)
            time.sleep(sleep_time)

        except:
            log_file.write(traceback.format_exc())
            log_file.write("\n")
            flush(log_file)
            traceback.print_exc()

            time.sleep(30)


if __name__ == "__main__":
    main()