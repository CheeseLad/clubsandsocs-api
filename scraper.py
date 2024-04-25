import requests
from bs4 import BeautifulSoup

def scrape_events(site, society):
  data = {}
  events = {}
  URL = f"https://{site}/society/{society}"
  headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"} 
  r = requests.get(url=URL, headers=headers) 
  soup = BeautifulSoup(r.content, 'html5lib')
  events_data = soup.find('div', attrs = {'id':'events'})
  event_count = events_data.find('span', attrs = {'class':'float-right badge badge-light'}).text
  event_table = events_data.find('div', attrs = {'class':'table-responsive'})
  events_info_list = event_table.find_all('tr', attrs={'class':'show_info pointer'})
  events_info_hidden = event_table.find_all('tr', attrs={'class':'d-none'})

  for i in range(0, len(events_info_list) - 1, 2):
    event_info = events_info_list[i]
    try:
      event_image = event_info.find('img')['src']
    except:
      event_image = None
    event_name = event_info.find('th', attrs={'class': 'h5 align-middle'}).text.strip()
    events[i // 2] = {'name': event_name, 'image': event_image}

  for i in range(1, len(events_info_list), 2):
    event_info = events_info_list[i]
    event_data = event_info.find_all('td', attrs={'class': 'text-center align-middle'})
    events[i // 2]['start'] = event_data[1].find('b').text
    events[i // 2]['end'] = event_data[2].find('b').text
    events[i // 2]['cost'] = event_data[3].find('b').text
    events[i // 2]['capacity'] = event_data[4].find('b').text
    events[i // 2]['type'] = event_data[5].find('b').text
    events[i // 2]['location'] = events_info_hidden[i].find('b').text
    events[i // 2]['description'] = events_info_hidden[i].find('p').text
    
  data['event_count'] = event_count
  data['events'] = events                                                                                           
  return data



def scrape_committee(site, society):
  data = {}
  committee_list = {}
  URL = f"https://{site}/society/{society}"
  headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"} 
  r = requests.get(url=URL, headers=headers) 
  soup = BeautifulSoup(r.content, 'html5lib')
  committee_table = soup.find('div', attrs = {'id':'committee_table'})
  committee_names = committee_table.find_all('th')
  committee_roles = committee_table.find_all('td')
  data['committee_count'] = len(committee_names)
  i = 0
  for name, role in zip(committee_names, committee_roles):
    committee_list[i] = {'position': name.text.strip(), 'name': role.text.strip()}
    i += 1
  data['committee'] = committee_list
  return data

def scrape_gallery(site, society):
  data = {}
  URL = f"https://{site}/society/{society}"
  headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"} 
  r = requests.get(url=URL, headers=headers) 
  soup = BeautifulSoup(r.content, 'html5lib')
  gallery = soup.find('div', attrs = {'class':'row photo_gallery mt-5 overflow-auto'})
  images = gallery.find_all('img')
  data['image_count'] = len(images)
  data['images'] = [img['src'] for img in images]
  return data

