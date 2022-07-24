import requests, re, time, random, threading, os
from threading import Thread
from colorama import init, Fore
init()

try:
    os.mkdir('clothes')
except: pass

lock = threading.Lock()
keyword = input('Enter keyword: ')
maximumMembers = 5000000
totalAssets = []
alreadyDone = []

def scrapeGroup(groupId):
    global totalAssets
    pageCursor = ''
    while pageCursor != None:
        try:
            r = requests.get(f'https://catalog.roblox.com/v1/search/items?category=All&creatorTargetId={groupId}&creatorType=Group&cursor={pageCursor}&limit=100&sortOrder=Desc').json()
            if 'data' in r:
                if len(r['data']) != 0:
                    currentAmount = 0
                    [(totalAssets.append(asset['id']), currentAmount := currentAmount + 1) for asset in r['data'] if asset['itemType'] == 'Asset']
                    with lock: print(f'[{Fore.MAGENTA}+{Fore.WHITE}] Collected {Fore.MAGENTA}{currentAmount} {Fore.WHITE}assets from {groupId}')
                    pageCursor = r['nextPageCursor']
                else:
                    with lock: print(f'[{Fore.MAGENTA}+{Fore.WHITE}] Group has no clothes >{Fore.MAGENTA} {groupId}{Fore.WHITE}')
                    return None
            else:
                with lock: print(f'[{Fore.YELLOW}-{Fore.WHITE}] Finding assets within group was ratelimited, retrying in {Fore.YELLOW}1{Fore.WHITE} minute')
                time.sleep(60)
        except Exception as err:
            print(err)
            time.sleep(60)
            continue

def downloadClothes():
    global alreadyDone
    while True:
        for assetId in totalAssets:
            if assetId not in alreadyDone:
                alreadyDone.append(assetId)
                try:
                    r = requests.get(re.findall(r'<url>(.+?)(?=</url>)', requests.get(f'https://assetdelivery.roblox.com/v1/asset?id={assetId}').text.replace('http://www.roblox.com/asset/?id=', 'https://assetdelivery.roblox.com/v1/asset?id='))[0]).content
                    if len(r) >= 7500:
                        with lock: print(f'[{Fore.GREEN}+{Fore.WHITE}] Downloaded asset > {Fore.GREEN}{assetId}{Fore.WHITE}')
                        with open(f'clothes/{assetId}.png', 'wb') as f:
                            f.write(r)
                    else:
                        with lock: print(f'[{Fore.RED}+{Fore.WHITE}] Unable to download asset > {Fore.RED}{assetId}{Fore.WHITE}')
                except:
                    with lock: print(f'[{Fore.RED}+{Fore.WHITE}] Unable to download asset > {Fore.RED}{assetId}{Fore.WHITE}')
                    pass
                totalAssets.remove(assetId)

def findGroups():
    pageCursor = ''
    while pageCursor != None:
        try:
            r = requests.get(f'https://groups.roblox.com/v1/groups/search?cursor={pageCursor}&keyword={keyword}&limit=100&prioritizeExactMatch=true&sortOrder=Asc').json()
            if 'data' in r:
                for group in r['data']:
                    if group['memberCount'] <= maximumMembers:
                        with lock: print(f'[{Fore.LIGHTCYAN_EX}-{Fore.WHITE}] Group found > {Fore.LIGHTCYAN_EX}{group["name"]}{Fore.WHITE}')
                        scrapeGroup(group['id'])
                    else:
                        pass
                        #with lock: print(f'[{Fore.LIGHTCYAN_EX}-{Fore.WHITE}] Group skipped > {Fore.LIGHTCYAN_EX}{group["memberCount"]}{Fore.WHITE} Members')
                pageCursor = r['nextPageCursor']
            else:
                with lock: print(f'[{Fore.YELLOW}-{Fore.WHITE}] Finding groups was ratelimit, retrying in {Fore.YELLOW}1{Fore.WHITE} minute')
                time.sleep(60)
        except Exception as err:
            print(err)
            time.sleep(60)
            continue

threading.Thread(target=findGroups).start()
time.sleep(5)
for i in range(50):
    threading.Thread(target=downloadClothes).start()
