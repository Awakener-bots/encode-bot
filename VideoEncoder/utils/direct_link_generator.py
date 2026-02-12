import json
import re
import urllib.parse
from base64 import standard_b64encode
from os import popen
from random import choice
from urllib.parse import urlparse

import cloudscraper
try:
    import lk21
except Exception:
    lk21 = None
import requests
from bs4 import BeautifulSoup
try:
    from js2py import EvalJs
except (ImportError, RuntimeError):
    EvalJs = None

class DirectDownloadLinkException(Exception):
    pass

def direct_link_generator(text_url: str):
    if 'youtube.com' in text_url or 'youtu.be' in text_url:
        raise DirectDownloadLinkException(f"ERROR: NO YTDL")
    elif 'dood.to' in text_url or 'yuudrive.' in text_url or 'pdisk.' in text_url or 'Pdisk.' in text_url or 'nitroflare.' in text_url:
        raise DirectDownloadLinkException('ERROR: These Links Are Not Supported')
    elif any(f'{i}:/' in text_url and text_url.endswith("/") for i in range(7)):
        raise DirectDownloadLinkException('ERROR: Bot can\'t download An Index Folder')
    elif '?a=view' in text_url:
        return text_url.replace("?a=view", "")
    elif 'zippyshare.com' in text_url:
        return zippy_share(text_url)
    elif 'yadi.sk' in text_url:
        return yandex_disk(text_url)
    elif 'cloud.mail.ru' in text_url:
        return cm_ru(text_url)
    elif 'mediafire.com' in text_url:
        return mediafire(text_url)
    elif 'osdn.net' in text_url:
        return osdn(text_url)
    elif 'github.com' in text_url:
        return github(text_url)
    elif 'hxfile.co' in text_url:
        return hxfile(text_url)
    elif 'anonfiles.com' in text_url:
        return anonfiles(text_url)
    elif 'letsupload.io' in text_url:
        return letsupload(text_url)
    elif any(x in text_url for x in ['fembed.net', 'fembed.com', 'femax20.com', 'fcdn.stream', 'feurl.com', 'naniplay.nanime.in', 'naniplay.nanime.biz', 'naniplay.com', 'layarkacaxxi.icu']):
        return fembed(text_url)
    elif any(x in text_url for x in ['sbembed.com', 'streamsb.net', 'sbplay.org']):
        return sbembed(text_url)
    elif 'racaty.net' in text_url:
        return racaty(text_url)
    elif '1drv.ms' in text_url:
        return onedrive(text_url)
    elif 'pixeldrain.com' in text_url:
        return pixeldrain(text_url)
    elif 'antfiles.com' in text_url:
        return antfiles(text_url)
    elif 'streamtape.com' in text_url:
        return streamtape(text_url)
    elif 'bayfiles.com' in text_url:
        return anonfiles(text_url)
    elif '1fichier.com' in text_url:
        return fichier(text_url)
    elif 'solidfiles.com' in text_url:
        return solidfiles(text_url)
    else:
        return None

def zippy_share(url: str) -> str:
    link = re.findall("https:/.(.*?).zippyshare", url)[0]
    response_content = (requests.get(url)).content
    bs_obj = BeautifulSoup(response_content, "lxml")

    try:
        js_script = bs_obj.find("div", {"class": "center", }).find_all("script")[1]
    except:
        js_script = bs_obj.find("div", {"class": "right", }).find_all("script")[0]

    js_content = re.findall(r'\.href.=."/(.*?)";', str(js_script))
    js_content = 'var x = "/' + js_content[0] + '"'

    if EvalJs is None:
        return "ERROR: js2py not functional on this Python version"
    
    evaljs = EvalJs()
    setattr(evaljs, "x", None)
    evaljs.execute(js_content)
    js_content = getattr(evaljs, "x")

    return f"https://{link}.zippyshare.com{js_content}"

def yandex_disk(url: str) -> str:
    try:
        text_url = re.findall(r'\bhttps?://.*yadi\.sk\S+', url)[0]
    except IndexError:
        return "`No Yandex.Disk links found`\n"
    api = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    try:
        dl_url = requests.get(api.format(text_url)).json()['href']
        return dl_url
    except KeyError:
        raise DirectDownloadLinkException("`Error: File not found / Download limit reached`\n")

def cm_ru(url: str) -> str:
    try:
        text_url = re.findall(r'\bhttps?://.*cloud\.mail\.ru\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No cloud.mail.ru links found`\n")
    command = f'vendor/cmrudl.py/cmrudl -s {text_url}'
    result = popen(command).read()
    result = result.splitlines()[-1]
    try:
        data = json.loads(result)
    except json.decoder.JSONDecodeError:
        raise DirectDownloadLinkException("`Error: Can't extract the link`\n")
    return data['download']

def mediafire(url: str) -> str:
    try:
        text_url = re.findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No MediaFire links found`\n")
    page = BeautifulSoup(requests.get(text_url).content, 'lxml')
    info = page.find('a', {'aria-label': 'Download file'})
    return info.get('href')

def osdn(url: str) -> str:
    osdn_link = 'https://osdn.net'
    try:
        text_url = re.findall(r'\bhttps?://.*osdn\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No OSDN links found`\n")
    page = BeautifulSoup(requests.get(text_url, allow_redirects=True).content, 'lxml')
    info = page.find('a', {'class': 'mirror_link'})
    text_url = urllib.parse.unquote(osdn_link + info['href'])
    mirrors = page.find('form', {'id': 'mirror-select-form'}).findAll('tr')
    urls = []
    for data in mirrors[1:]:
        mirror = data.find('input')['value']
        urls.append(re.sub(r'm=(.*)&f', f'm={mirror}&f', text_url))
    return urls[0]

def github(url: str) -> str:
    try:
        text_url = re.findall(r'\bhttps?://.*github\.com.*releases\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No GitHub Releases links found`\n")
    download = requests.get(text_url, stream=True, allow_redirects=False)
    try:
        return download.headers["location"]
    except KeyError:
        raise DirectDownloadLinkException("`Error: Can't extract the link`\n")

def onedrive(link: str) -> str:
    link_without_query = urlparse(link)._replace(query=None).geturl()
    direct_link_encoded = str(standard_b64encode(bytes(link_without_query, "utf-8")), "utf-8")
    direct_link1 = f"https://api.onedrive.com/v1.0/shares/u!{direct_link_encoded}/root/content"
    resp = requests.head(direct_link1)
    if resp.status_code != 302:
        return "ERROR: Unauthorized link, the link may be private"
    return resp.next.url

def hxfile(url: str) -> str:
    if lk21 is None:
        raise DirectDownloadLinkException("lk21 package not functional")
    bypasser = lk21.Bypass()
    return bypasser.bypass_filesIm(url)

def anonfiles(url: str) -> str:
    if lk21 is None:
        raise DirectDownloadLinkException("lk21 package not functional")
    bypasser = lk21.Bypass()
    return bypasser.bypass_anonfiles(url)

def letsupload(url: str) -> str:
    if lk21 is None:
        raise DirectDownloadLinkException("lk21 package not functional")
    try:
        link = re.findall(r'\bhttps?://.*letsupload\.io\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Letsupload links found\n")
    bypasser = lk21.Bypass()
    return bypasser.bypass_url(link)

def fembed(link: str) -> str:
    if lk21 is None:
        return "ERROR: lk21 package not functional"
    bypasser = lk21.Bypass()
    dl_url = bypasser.bypass_fembed(link)
    lst_link = []
    for i in dl_url:
        lst_link.append(dl_url[i])
    return lst_link[-1]

def sbembed(link: str) -> str:
    if lk21 is None:
        return "ERROR: lk21 package not functional"
    bypasser = lk21.Bypass()
    dl_url = bypasser.bypass_sbembed(link)
    lst_link = []
    for i in dl_url:
        lst_link.append(dl_url[i])
    return lst_link[-1]

def pixeldrain(url: str) -> str:
    url = url.strip("/ ")
    file_id = url.split("/")[-1]
    info_link = f"https://pixeldrain.com/api/file/{file_id}/info"
    dl_link = f"https://pixeldrain.com/api/file/{file_id}"
    resp = requests.get(info_link).json()
    if resp["success"]:
        return dl_link
    else:
        raise DirectDownloadLinkException("ERROR: Cant't download due {}.".format(resp.text["value"]))

def antfiles(url: str) -> str:
    if lk21 is None:
        raise DirectDownloadLinkException("lk21 package not functional")
    bypasser = lk21.Bypass()
    return bypasser.bypass_antfiles(url)

def streamtape(url: str) -> str:
    if lk21 is None:
        raise DirectDownloadLinkException("lk21 package not functional")
    bypasser = lk21.Bypass()
    return bypasser.bypass_streamtape(url)

def racaty(url: str) -> str:
    try:
        link = re.findall(r'\bhttps?://.*racaty\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Racaty links found\n")
    scraper = cloudscraper.create_scraper()
    r = scraper.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    op = soup.find("input", {"name": "op"})["value"]
    ids = soup.find("input", {"name": "id"})["value"]
    rpost = scraper.post(url, data={"op": op, "id": ids})
    rsoup = BeautifulSoup(rpost.text, "lxml")
    return rsoup.find("a", {"id": "uniqueExpirylink"})["href"].replace(" ", "%20")

def fichier(link: str) -> str:
    regex = r"^([http:\/\/|https:\/\/]+)?.*1fichier\.com\/\?.+"
    if not re.match(regex, link):
        raise DirectDownloadLinkException("ERROR: The link you entered is wrong!")
    if "::" in link:
        pswd = link.split("::")[-1]
        url = link.split("::")[-2]
    else:
        pswd, url = None, link
    try:
        req = requests.post(url, data={"pass": pswd} if pswd else None)
    except:
        raise DirectDownloadLinkException("ERROR: Unable to reach 1fichier server!")
    if req.status_code == 404:
        raise DirectDownloadLinkException("ERROR: File not found!")
    soup = BeautifulSoup(req.content, 'lxml')
    if (btn := soup.find("a", {"class": "ok btn-general btn-orange"})):
        return btn["href"]
    
    warns = soup.find_all("div", {"class": "ct_warn"})
    if not warns:
        raise DirectDownloadLinkException("ERROR: Error generating 1fichier link!")
    
    warn_text = str(warns[-1]).lower()
    if "you must wait" in warn_text:
        nums = [int(w) for w in warn_text.split() if w.isdigit()]
        wait = f"{nums[0]} minute" if nums else "a few minutes"
        raise DirectDownloadLinkException(f"ERROR: 1fichier limit reached. Wait {wait}.")
    elif "protect access" in warn_text:
        raise DirectDownloadLinkException("ERROR: Password required! Use ::password format.")
    elif "bad password" in warn_text:
        raise DirectDownloadLinkException("ERROR: Wrong password!")
    raise DirectDownloadLinkException("ERROR: 1fichier error!")

def solidfiles(url: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0'}
    source = requests.get(url, headers=headers).text
    options = str(re.search(r'viewerOptions\'\,\ (.*?)\)\;', source).group(1))
    return json.loads(options)["downloadUrl"]

def useragent():
    useragents = BeautifulSoup(requests.get('https://developers.whatismybrowser.com/useragents/explore/operating_system_name/android/').content, 'lxml').findAll('td', {'class': 'useragent'})
    return choice(useragents).text
