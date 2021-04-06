#################################
##### Name: Suhas Potluri
##### Uniqname: spotlu
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category,name,address,zipcode,phone):
        self.category=category
        self.name=name
        self.address=address
        self.zipcode=zipcode
        self.phone=phone
    def info(self):
        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    statesDict={}
    r=requests.get('https://www.nps.gov/findapark/index.htm')
    soup=BeautifulSoup(r.text,'html.parser')
    states=soup.find_all('area')
    for state in states:
        link=state['href']
        state=state['alt'].lower()
        statesDict[state]='https://www.nps.gov'+link
    return statesDict

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    r=requests.get(site_url)
    soup=BeautifulSoup(r.text,'html.parser')
    name=soup.find_all('a',{'class':'Hero-title'})[0].text
    category=soup.find_all('span',{'class':'Hero-designation'})[0].text
    #streetAddress
    address=soup.find_all('span',{'itemprop':'addressLocality'})[0].text
    state=soup.find_all('span',{'itemprop':'addressRegion'})[0].text
    zipcode=soup.find_all('span',{'itemprop':'postalCode'})[0].text.strip()
    phone=soup.find_all('span',{'itemprop':'telephone'})[0].text.strip('\n')
    address=address+', '+state
    return NationalSite(category,name,address,zipcode,phone)

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    sitesList=[]
    r=requests.get(state_url)
    soup=BeautifulSoup(r.text,'html.parser')
    sites=soup.find_all('ul',{'id':'list_parks'})[0].find_all('a')
    for site in sites:
        if 'http' not in site['href']:
            sitesList.append(get_site_instance('https://www.nps.gov'+site['href']))
    return sitesList

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    radius=10
    maxMatches=10
    ambiguities="ignore"
    outFormat="json"
    params={'radius':radius,'maxMatches':maxMatches,'ambiguities':ambiguities,'outFormat':outFormat,'key':secrets.API_KEY,"origin":site_object.address}
    r=requests.get("http://www.mapquestapi.com/search/v2/radius",params=params)
    results=r.json()
    return results


if __name__ == "__main__":
    states=build_state_url_dict()
    run=True
    while run:
        inp=input('Enter a state name or "exit": \n').lower()
        if inp in states:
            sites=get_sites_for_state(states[inp])
            print("--------------------------------------------")
            print("List of national sites in "+inp.capitalize())
            print("--------------------------------------------")
            
            run2=True
            while run2:
                x=1
                for site in sites:
                    print(f"[{x}] {site.info()}")
                    x+=1
                print('Choose the number for detail search or "exit" or "back" ')
                inp2=input()
                if inp2=="back":
                    break
                elif inp2=="exit":
                    quit()
                else:
                    try:
                        num=int(inp2)
                        try:
                            data=get_nearby_places(sites[num-1])['searchResults']
                            print(f'Places near {sites[num-1].name}:')
                            for i in data:
                                print(f"- {i['name']} ({i['fields'].get('group_sic_code_name','no category')}): {i['fields'].get('address','no address')}, {i['fields'].get('state','no state')} {i['fields'].get('postal_code','no postal code')}")
                    
                        except:
                            print('No places nearby')
                            
                    except:
                        print('[Error} Invalid input')

        elif inp=="exit":
            break
        else:
            print('State not found')
