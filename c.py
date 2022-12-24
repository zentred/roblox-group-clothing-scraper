import requests, re, time, random, threading, os, ctypes, json
from threading import Thread
from colorama import init, Fore
init()

with open('config.json') as config:
    config = json.load(config)

with open('checked_groups.txt', 'a') as q:
    q.close()

try: os.mkdir('clothes')
except: pass

checked_groups = open('checked_groups.txt').read().splitlines()

class Bot:

    def __init__(self):
        self.lock = threading.Lock()
        self.checked = 0
        self.scraped = 0
        self.downloaded = 0
        self.search()

    def title(self, status):
        ctypes.windll.kernel32.SetConsoleTitleW(
            f'Checked Groups: {self.checked} / Scraped Assets: {self.scraped} / Downloaded Assets: {self.downloaded} / Status: {status}'
        )

    def search(self):
        cursor = ''
        while cursor != None:
            resp = requests.get(
                f'https://groups.roblox.com/v1/groups/search?cursor={cursor}&keyword={config["keyword"]}&limit=100&prioritizeExactMatch=true&sortOrder=Asc'
            )
            if resp.status_code == 200:
                for i in resp.json()['data']:
                    if config['minimumMembers'] <= i['memberCount'] <= config['maximumMembers']:
                        if str(i['id']) not in checked_groups:
                            self.scrape(i['id'])
                cursor = resp.json()['nextPageCursor']
            else:
                self.title('Ratelimited')
                time.sleep(60)

    def scrape(self, groupid):
        cursor, assets = '', []
        while cursor != None:
            resp = requests.get(
                f'https://catalog.roblox.com/v1/search/items?category=All&creatorTargetId={groupid}&creatorType=Group&cursor={cursor}&limit=100&sortOrder=Desc'
            )
            if resp.status_code == 200:
                if resp.json()['data'] != []:
                    for asset in resp.json()['data']:
                        if asset['itemType'] == 'Asset':
                            assets.append(asset['id'])
                            self.scraped += 1
                            self.title('Running')
                cursor = resp.json()['nextPageCursor']
            else:
                self.title('Ratelimited')
                time.sleep(60)
        self.checked += 1
        self.title('Running')

        threads = [threading.Thread(target=self.download, args=[assets[i::25]]) for i in range(25)]
        for i in threads:
            i.start()
        for i in threads:
            i.join()

        with open('checked_groups.txt', 'a') as q:
            q.writelines(f'{groupid}\n')

    def download(self, assets):
        for assetid in assets:
            try:
                url = re.search('<url>(.*?)</url>', requests.get(f'https://assetdelivery.roblox.com/v1/asset?id={assetid}', timeout=5).text).group(1).replace('http://www.roblox.com/asset/?id=', 'https://assetdelivery.roblox.com/v1/asset?id=')
                resp = requests.get(url, timeout=5).content
                if len(resp) >= 7500:
                    with open(f'clothes/{assetid}.png', 'wb') as f:
                        f.write(resp)
                    self.downloaded += 1
                    self.title('Running')
            except Exception as err:
                print(err)
                pass

Bot()
input("    Unable to find any groups + assets to copy? Try increasing the maximum members\n\n    Press enter to exit.")
