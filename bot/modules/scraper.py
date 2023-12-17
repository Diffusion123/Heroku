import base64
import json
import urllib.parse
import requests
from asyncio import sleep
import re 
from urllib.parse import unquote, urlparse
from bs4 import BeautifulSoup
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage, deleteMessage
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException

async def bypass(_, message):
    args = message.text.split()
    link = args[1] if len(args) > 1 else ''
    domain = urlparse(link).hostname
    if not domain:
        raise DirectDownloadLinkException("ERROR: Invalid URL")
    if "kayoanime.com" in link:
        await kayoanime(link, message)
    elif "linkbuzz.click" in link:
        await linkbuzz(link, message)
    elif "animeflix.website" in link:
        await animeflix(link, message)
    elif "animeremux.xyz" in link:
        await animeremux(link, message)
    elif "atishmkv.pro" in link:
        await atishmkv(link, message)
    elif "kissasian.cz" in link:
        await kissasian(link, message)    
    else:       
        return

def get_redirected_url(url):
    response = requests.head(url, allow_redirects=True)
    return response.url

def soup_res(link):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(link, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')

def final(new_url,t):
    soup = soup_res(new_url)
    link_list = soup.find_all('a', href=re.compile(r"https://(.*drive.*|.*yandex.*).*.*\/"))
    for k in link_list:
        drive = k['href']
        title = " ".join(t.split('/')[0].split('-'))
        return f"{title}\n <a href='{drive}'>Download Link</a>\n"

async def kissasian(link, message):
    reply = await sendMessage(message, "<code>Getting Links</code>")
    soup = soup_res(link)
    ep_links = soup.find_all('a', href=re.compile(r'.*episode.*'))
    urls = []
    for ep in ep_links:
        new = f"https://kissasian.cz{ep['href']}"
        urls.append(new)

    for reversed_url in reversed(urls):
        soup = soup_res(reversed_url)
        links = soup.find_all('option', value=re.compile(r'.*play.php.*'))
        result = ""
        for r in links:
            t = r['value'].replace("play.php", "download")
            result += f"https:{t}\n\n"
            await editMessage(reply, result)
            if len(result) > 4000:
                sent = await sendMessage(reply, result)
                result = ""
                await deleteMessage(reply)

async def kayoanime(link, message):
    reply = await sendMessage(message, "Getting Links........")
    soup = soup_res(link)
    links = soup.find_all('a', href=re.compile(r'https://drive.google.com/.*'))
    result = ""
    for l in links:
        url_link = l['href']
        title = l.get_text()  # This gets the text within the <a> tag
        result += f"{title}  ---  <a href='{url_link}'>Gdrive link</a>\n\n"
    await editMessage(reply, result)
   
async def linkbuzz(link, message):
    reply = await sendMessage(message, "Requesting linkbuzz.click for links")
    soup = soup_res(link)
    links = soup.find_all('a',  href=re.compile(r'https:(.*gdtot.*|.*filepress.*|.*gdflix).*/\.*'))
    result = ""
    for c in links:
        url_link = c['href']
        title = c.get_text()
        if re.match(r'https:(.*gdtot.*|.*filepress.*|.*gdflix).*/\.*', url_link):
            new_url = get_redirected_url(url_link)
            result += f"\n\n{title} ---- <a href='{new_url}'>Download Link</a>\n\n"
            await sendMessage(reply, result)
            await deleteMessage(reply)
        
async def animeremux(link, message):
    reply = await sendMessage(message, "Getting Links........")
    soup = soup_res(link)
    links = soup.find_all('a', {'class': "shortc-button small blue"}, href=re.compile(r'.*\/'))
    count = 0
    r = ""
    for l in links:
        result = l['href']
        allow_redirect = not re.match(r'https://drive.google.com.*\/', result)
        txt = soup.find_all('title')
        s = txt[0].text
        txt = l.text
        t = requests.get(result, allow_redirects=allow_redirect)
        r += f"<a href='{t.url}'>{txt}</a>\n\n"
        await editMessage(reply, r)
        if len(result) > 4000:
            sent = await sendMessage(reply, r)
            r = ""
            await deleteMessage(reply)

async def atishmkv(link, message):
    reply = await sendMessage(message, "Getting Links from atishmkv.pro")
    soup = soup_res(link)
    list = soup.find_all('a', {'class': "button button-shadow"}, href=re.compile(r'.*\/'))
    result = ""
    for links in list:
        text = links.get_text()
        f = links.get('href', '')
        result += f"\n\n{text}\n\n"
        sub_soup = soup_res(f)
        for a in sub_soup.find_all('a', href=re.compile(r'(?<=\?goto=)[^&]+?')):
            href_links = a.get('href', '')
            new_link = requests.get(href_links, allow_redirects=True)
            new = new_link.url
            if urlparse(new).hostname:
                hostnames = urlparse(new).hostname
                result += f"<a href='{new}'>{hostnames.upper()}</a>   "  # Append to 'r' instead of re
                await editMessage(reply, result)
                if len(result) > 4000:
                    sent = await sendMessage(reply, result)
                    result = ""
                    await deleteMessage(reply)
                    
async def animeflix(link, message):
    reply = await sendMessage(message, "Getting Links from animeflix.website")
    soup = soup_res(link)
    href_list = soup.find_all('a', class_='wb_button', href=re.compile(fr".*episode.*\/"))
    if href_list:
        for text in href_list:
            result = ""
            t = text['href']
            new_url = f"https://{link.split('/')[2]}/{t}"
            result += final(new_url,t)
            await sendMessage(reply, result)
    else:
        href_list = soup.find_all('a', class_='wb_button', href=re.compile(fr".*drive.*\/"))
        for span in href_list:
            result = ""
            title1 = span['title']
            l = span['href']
            result += f"{title1}\n <a href='{l}'>Download Link</a>\n\n"
            await sendMessage(reply, result)
    await deleteMessage(reply)

def func(link, payload, auth_header):
    headers = {
        "Authorization": auth_header,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; M2006C3LI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36",
        "Referer": link
    }
    encrypted_response = requests.post(link, data=payload, headers=headers)  # Corrected variable name
    decoded_data = base64.b64decode(encrypted_response.text[::-1][24:-20]).decode("utf-8")
    return json.loads(decoded_data)

def get_readable_file_size(file_size):
    file_size = int(file_size)
    if file_size < 1024:
        return f"{file_size} Bytes"
    elif 1024 <= file_size < 1024**2:
        return f"{file_size / 1024:.2f} KB"
    elif 1024**2 <= file_size < 1024**3:
        return f"{file_size / (1024**2):.2f} MB"
    elif 1024**3 <= file_size < 1024**4:
        return f"{file_size / (1024**3):.2f} GB"

async def scraper(_, message):  
    args = message.text.split()
    link = args[1] if len(args) > 1 else ''
    reply = await sendMessage(message, "Extracting Index...")    
    link = f"{link}/" if link and link[-1] != '/' else link  # Added a check for an empty link
    auth_header = f"Basic {base64.b64encode('username:password'.encode()).decode().strip()}"
    payload = {"page_token": "", "page_index": 0}
    
    try:
        decrypted_response = func(link, payload, auth_header)
        result = ""
        
        if "data" in decrypted_response and "files" in decrypted_response["data"]:
            for file in decrypted_response["data"]["files"]:
                if file["mimeType"] != "application/vnd.google-apps.folder":
                    size = get_readable_file_size(file["size"])
                    result += f"Name: {urllib.parse.unquote(file['name'])}  [{size}]\n <a href='https://drive.google.com/file/d/{urllib.parse.quote(file['id'])}'>Gdrive link</a>   <a href='{link}{urllib.parse.quote(file['name'])}'>Index link</a>\n\n"
                    await editMessage(reply, result)
                    if len(result) > 4000:
                        sent = await sendMessage(reply, result)
                        result = ""
                        await deleteMessage(reply)


        if not result:
            f_result = ""
            folders = decrypted_response['data']['files']
            for folder in folders:              
                folder_url = f"https://drive.google.com/drive/folders/{folder['id']}"        
                file_urls = f"{link}{urllib.parse.quote(folder['name'])}/"
                f_result += f"Name: {folder['name']}\n<a href='{folder_url}'>Folder Link</a>   <a href='{file_urls}'>Index Folder</a>\n\n"
                await editMessage(reply, f_result)
                if len(f_result) > 4000:
                    sent = await sendMessage(reply, f_result)
                    f_result = ""
                    await deleteMessage(reply)
        
    except requests.exceptions.RequestException as e:
        # Handle exception appropriately
        print(f"Request Exception: {e}")

async def transcript(url: str, DOMAIN: str, ref: str, sltime,) -> str:
    reply = await sendMessage("Bypassing {ur}")
    code = url.rstrip("/").split("/")[-1]
    cget = create_scraper(allow_brotli=False).request
    resp = cget("GET", f"{DOMAIN}/{code}", headers={"referer": ref})
    soup = BeautifulSoup(resp.content, "html.parser")
    data = { inp.get('name'): inp.get('value') for inp in soup.find_all("input") }
    await asleep(sltime)
    resp = cget("POST", f"{DOMAIN}/links/go", data=data, headers={ "x-requested-with": "XMLHttpRequest" })
    result = resp.json()['url']
    await editMessage(reply, result)

bot.add_handler(MessageHandler(scraper, filters=command(BotCommands.ScraperCommand) & CustomFilters.sudo))
bot.add_handler(MessageHandler(bypass, filters=command(BotCommands.ByPassCommand) & CustomFilters.sudo))
