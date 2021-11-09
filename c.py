import requests, re, time, colorama, random, threading, os
from collections import Counter
from threading import Thread
from colorama import init, Fore, Back, Style
init()

threadc = 100

def divide(stuff):
    return [stuff[i::threadc] for i in range(threadc)]

def group_scrape(groupid):
    all = []
    total_scraped = 0
    cursor = ''
    while True:
        try:
            c = 0
            r = requests.get(f'https://catalog.roblox.com/v1/search/items?category=All&creatorTargetId={groupid}&creatorType=Group&cursor={cursor}&limit=100&sortOrder=Desc')
            assets = int(r.text.count('id'))
            total_scraped += assets
            for i in range(assets):
                assetid = r.json()['data'][c]['id']
                all.append(assetid)
                c += 1
            if assets == 100:
                print(Fore.CYAN + '[SCRAPING]' + Fore.CYAN + f' {assets} assets were scraped')
                cursor = r.json()['nextPageCursor']
            elif assets != 100:
                print(Fore.CYAN + '[SCRAPING]' + Fore.CYAN + f' {assets} assets were scraped')
                print(Fore.CYAN + '[COLLECTED]' + Fore.CYAN + f' {total_scraped} assets were scraped in total')
                return all
            time.sleep(2)
        except:
            print(f'Ratelimit may have occured: {r}')

def asset_download(asset_list):
    for asset_id in asset_list:
        try:
            r = requests.get(re.findall(r'<url>(.+?)(?=</url>)', requests.get(f'https://assetdelivery.roblox.com/v1/asset?id={asset_id}').text.replace('http://www.roblox.com/asset/?id=', 'https://assetdelivery.roblox.com/v1/asset?id='))[0]).content
            if len(r) >= 7500:
                print(Fore.GREEN + '[STEALER]' + Fore.GREEN + f' {asset_id} template was downloaded')
                with open(f'{asset_id}.png', 'wb') as f:
                    f.write(r)
        except:
            print(Fore.RED + '[STEALER]' + Fore.RED + f' {asset_id} template was not downloaded')

print(f'\n' + Fore.CYAN + '[GROUPID]' + Fore.CYAN + ' Enter Group ID:')
groupid = input('')
folder = groupid
asset_list = group_scrape(groupid)
time.sleep(1)
print(f'\n' + Fore.CYAN + '[STEALER]' + Fore.CYAN + ' Assets are being downloaded')
print(Fore.CYAN + '[STEALER]' + Fore.CYAN + ' GREEN = Downloaded')
print(Fore.CYAN + '[STEALER]' + Fore.CYAN + ' RED = Not Downloaded\n')

threads = []
for i in range(threadc):
    threads.append(Thread(target=asset_download,args=[divide(asset_list)[i]]))
    threads[i].start()
for thread in threads:
    thread.join()
