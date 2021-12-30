import requests, re, time, colorama, random, threading, os, sys
from collections import Counter
from threading import Thread
from colorama import init, Fore, Back, Style
init()

threadc = 50
red = Fore.RED
green = Fore.GREEN
blue = Fore.LIGHTBLUE_EX

def group_scrape():
    all = []
    total_scraped = 0
    cursor = ''

    while True:
        r = requests.get(f'https://catalog.roblox.com/v1/search/items?category=All&creatorTargetId={groupid}&creatorType=Group&cursor={cursor}&limit=100&sortOrder=Desc', cookies={'.ROBLOSECURITY': '_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_1F0F7B7FF8DAFFE7B8FE2E1DF493549CD5BC0A83972EDB982D3959DDDD66C83B3F1B2E96066A00A60ED98678382FB279035D1036AF18984A491B11D07D81AF8830CF8FC37B12F262CECA04AF6BEA9E3D2F0E9449132E653A21271F59FB981C0DB3FDD8BF5F577D7E02458FE21C6C138B688692CE1A7AA1EFBC10455BB3A88541829B03E66BDFBDB867A0B6F1BF7AE862F3E64FE28FAE2785C28A88F397F045411CA1DFC95EE4D7D1FE3D4B6D1D84D94496226BE895ED7C6546D39574621E75889EC192704250C2465F64039EE98A17DD3CD03562588EA2BA8D262EC08FAEE13A7F155D6AE1F5A2FAD5C47E18056D67EDB78B6B8A60784AFA3DFF2BB47184C441429C369A5F97D16094FC2F8CF182F00CC2C75DD19932FE762B8D005377C93FFFE77FF2322BFC7C31DF0856544C0129E4A325132672DA77F6EA6196E389E1157BFD1C95195D4EC6371A60DEF0BAA1B975463D1D6E'}).json()
        assets = len(r['data'])

        if assets == 100:
            cursor = r['nextPageCursor']
            for i in range(assets):
                cid = r['data'][i]['id']
                if r['data'][i]['itemType'] == 'Asset': all.append(cid)
                sys.stdout.write(f'{blue}[SCRAPED] {cid}\n')

        elif assets != 100:
            for i in range(assets):
                cid = r['data'][i]['id']
                if r['data'][i]['itemType'] == 'Asset': all.append(cid)
                sys.stdout.write(f'{blue}[SCRAPED] {cid}\n')
            return all

def asset_download(asset_list):
    for asset_id in asset_list:
        try:
            r = requests.get(re.findall(r'<url>(.+?)(?=</url>)', requests.get(f'https://assetdelivery.roblox.com/v1/asset?id={asset_id}').text.replace('http://www.roblox.com/asset/?id=', 'https://assetdelivery.roblox.com/v1/asset?id='))[0]).content
            if len(r) >= 7500:
                sys.stdout.write(f'{green}[DOWNLOADER] {asset_id} template was downloaded\n')
                with open(f'{groupid}/{asset_id}.png', 'wb') as f:
                    f.write(r)
            else:
                sys.stdout.write(f'{red}[DOWNLOADER] {asset_id} template was not downloaded\n')
        except:
            sys.stdout.write(f'{red}[DOWNLOADER] {asset_id} template was not downloaded\n')


print(f'{blue}Enter Group ID:')
groupid = input('')
print('')

asset_list = group_scrape()

print(f'\n\n{blue}{len(asset_list)} asset templates are being downloaded\n{green}GREEN = Downloaded\n{red}RED = Not Downloaded\n')

time.sleep(1)

os.mkdir(groupid)
if len(asset_list) > 0:
    threads = []
    for i in range(threadc):
        threads.append(Thread(target=asset_download,args=[asset_list[i::threadc]]))
        threads[i].start()
