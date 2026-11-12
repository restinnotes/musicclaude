import requests,bs4,sys,urllib.parse,base64
q=' '.join(sys.argv[1:]); s=bs4.BeautifulSoup(requests.get('https://www.bing.com/search',params={'q':q},headers={'User-Agent':'Mozilla/5.0'},timeout=20).text,'html.parser')
for x in s.select('li.b_algo'):
 a=x.select_one('h2 a'); u=a.get('href') if a else ''
 if 'bing.com/ck/' in u:
  v=urllib.parse.parse_qs(urllib.parse.urlparse(u).query).get('u',[''])[0]
  if v.startswith('a1'): u=base64.b64decode(v[2:]+'===').decode(errors='replace')
 print('TITLE',a.get_text(' ',strip=True) if a else '','URL',u); print('TEXT',x.get_text(' ',strip=True)[:550])
