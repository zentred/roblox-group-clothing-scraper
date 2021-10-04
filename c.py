import requests
import collections
from collections import Counter
import re
import time
import colorama
import random
import threading
import os
import shutil
from threading import Thread
from colorama import init, Fore, Back, Style
init()

threadc = 100

groupz = open('groups.txt','r').read().splitlines()

proxies = open('proxies.txt','r').read().splitlines()
proxies = [{'https':'http://'+proxy} for proxy in proxies]


def divide(stuff):
    return [stuff[i::threadc] for i in range(threadc)]

def group_scrape(groupid):
    wow = []
    number = 0
    cursor = ''
    start = 'nextPageCursor":"'
    end = '","data"'
    req = requests.Session()
    r = req.get(f'https://catalog.roblox.com/v1/search/items?category=All&creatorTargetId={groupid}&creatorType=Group&cursor={cursor}&limit=100&sortOrder=Desc',proxies=random.choice(proxies)).text
    wow.append(r)
    first_amount = int(r.count('itemType'))
    print(Fore.CYAN + '[SCRAPING]' + Fore.CYAN + f' {first_amount} assets were scraped')
    number += first_amount
    if not '"nextPageCursor":null' in r:
        cursor = r.split(start)[1].split(end)[0]
        while True:
            try:
                r = req.get(f'https://catalog.roblox.com/v1/search/items?category=All&creatorTargetId={groupid}&creatorType=Group&cursor={cursor}&limit=100&sortOrder=Desc',proxies=random.choice(proxies)).text
                assets = int(r.count('itemType'))
                number += assets
                print(Fore.CYAN + '[SCRAPING]' + Fore.CYAN + f' {assets} assets were scraped')
                if not '"nextPageCursor":null' in r:
                    cursor = r.split(start)[1].split(end)[0]
                    wow.append(r)
                elif '"nextPageCursor":null' in r:
                    wow.append(r)
                    print(Fore.CYAN + '[COLLECTED]' + Fore.CYAN + f' {number} assets were scraped in total')
                    return wow
                elif assets == 0:
                    pass
            except:
                print('Scrape Failed')
    print(Fore.CYAN + '[COLLECTED]' + Fore.CYAN + f' {first_amount} assets were scraped in total')
    return wow

def collect_ids():
    the = open('save.txt','r').read().splitlines()
    for line in the:
        matches = re.findall('{"id":(.*?),"itemType"', line, re.DOTALL)
        with open('save.txt','w') as e:
            e.write('\n'.join(str(line) for line in matches))

def asset_download(the_ids):
    for asset_id in the_ids:
        with open(f'{asset_id}.png', 'wb') as f:
            try:
                f.write(requests.get(re.findall(r'<url>(.+?)(?=</url>)', requests.get(f'https://assetdelivery.roblox.com/v1/asset?id={asset_id}').text.replace('http://www.roblox.com/asset/?id=', 'https://assetdelivery.roblox.com/v1/asset?id='))[0]).content)
            except:
                print(Fore.RED + '[STEALER]' + Fore.RED + f' {asset_id} template was not downloaded')
            else:
                print(Fore.GREEN + '[STEALER]' + Fore.GREEN + f' {asset_id} template was downloaded')

def sort_files(folder):
    print(Fore.CYAN + '[SORT]' + Fore.CYAN + f' Templates are being sorted')
    source = os.path.join('C:\\Users\\Administrator\\Desktop\clothes')
    sort = os.path.join(f'C:\\Users\\Administrator\\Desktop\\clothes\\{folder}')
    dirName = f'{folder}'
    os.mkdir(dirName)
    for f in os.listdir(source):
        if f.endswith((".png",".jpg",".jpeg")):
            shutil.move(os.path.join(source, f), sort)

for groupid in groupz:
    folder = groupid
    assets = group_scrape(groupid)
    with open('save.txt','w') as e:
        e.writelines(assets)
    time.sleep(1)
    filtered_ids = collect_ids()
    time.sleep(1)
    the_ids = open('save.txt','r').read().splitlines()
    print(f'\n' + Fore.CYAN + '[STEALER]' + Fore.CYAN + ' Assets are being downloaded')
    print(Fore.CYAN + '[STEALER]' + Fore.CYAN + ' GREEN = Downloaded')
    print(Fore.CYAN + '[STEALER]' + Fore.CYAN + ' RED = Not Downloaded\n')


    threads = []
    for i in range(threadc):
        threads.append(Thread(target=asset_download,args=[divide(the_ids)[i]]))
        threads[i].start()
    for thread in threads:
        thread.join()

    sort_files(folder)
    print(Fore.GREEN + '[SORT]' + Fore.GREEN + f' Templates were sorted')
