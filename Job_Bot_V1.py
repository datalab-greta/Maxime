#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 14:21:55 2019

@author: maxime
"""
import pandas as pd
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup 
import datetime

url='https://candidat.pole-emploi.fr/offres/recherche?lieux=24R&motsCles=data&offresPartenaires=true&range=0-9&rayon=10&tri=0'

def simple_get(url):
    """
    Se connecte a l'url, si statut = 200 retourne le contenu ( en appelant is_good_response)
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Renvoie 200 si connection a l'url
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    retourne l'erreur
    """
    print(e)


def get_url(soup):
    """
    Recupère les urls une par une
    """
    urls = []
    for link in soup.find_all('h2', {'class': 'media-heading'}):
        partial_url = link.a.get('href')
        url = 'https://candidat.pole-emploi.fr' + partial_url
        urls.append(url)
    return urls


"""
stock les url dans une liste
"""
html=simple_get('https://candidat.pole-emploi.fr/offres/recherche?motsCles=ingenieur&offresPartenaires=true&range=0-9&rayon=10&tri=0')
soup= BeautifulSoup(html,'html.parser')
def get_nb(soup):
    nb=soup.find("h1").text
    idxnb=nb.index(' offre')
    nb=nb[0:idxnb]
    return int(nb)
    
listeUrl=[]
listeF = []
dico = {}

nbOffre=int(get_nb(soup))

if (nbOffre>150):
    nbpage=(nbOffre//150)+1
    url2=150
else:
    url2=nbOffre
url1=0

listeUrlT=[]
for i in range(nbpage):
    listeUrlT=[]
    
    url='https://candidat.pole-emploi.fr/offres/recherche?motsCles=ingenieur&offresPartenaires=true&range='+str(url1)+'-'+str(url2)+'&rayon=10&tri=0'
    uc=nbOffre-url2
    
    if (uc>150):
        url1+=150
        if (url1==url2):
            url1+=1
        url2+=150
    else:
        url1=url2+1
        url2=nbOffre
        
    html=simple_get(url)
    soup=BeautifulSoup(html, 'html.parser')
    allUrl=get_url(soup)
    listeUrlT.append(allUrl)
    for i in listeUrlT:
        listeUrl.append(i) 
c=0
               
        
for x in listeUrl:
    for i in x:
        """
        boucle qui envoie les urls une par une
        """
        skills=''
        xp=''
        liste=[]
    
        raw_html = simple_get(i)
        """
        on récupère les éléments qui nous interesse et on les nettoie
        """
        title = str(BeautifulSoup(raw_html, 'html.parser').find_all("h2")[1:2])
        title = title[31:len(title)].replace("\n</h2>]","")
        
        date = str(BeautifulSoup(raw_html, 'html.parser').find_all("span", itemprop={"datePosted"}))
        date = date[51:len(date)].replace("\n</span>]","") 
        
        secteur = str(BeautifulSoup(raw_html, 'html.parser').find_all("span", itemprop={"industry"}))
        secteur = secteur[27:len(secteur)].replace('</span>]','')
        
        address = str(BeautifulSoup(raw_html, 'html.parser').find_all("span", itemprop={"name"}))
        address = address[23:len(address)].split('<')[0]
        
        description = str(BeautifulSoup(raw_html, 'html.parser').find_all("div", itemprop={"description"}))
        description = description[70:len(description)].replace('</p></div>]','')
        
        competenceXp = str(BeautifulSoup(raw_html, 'html.parser').find_all('span', attrs={"class":"skill-name"}))    
        
        for x in competenceXp.split('span'):
            """
            on récupère les elements definit dans les elses dans des variables avant de les ajouter dans une liste
            """
            if ("skills" in x):
    
                skills += x+"|"
                skills = skills.replace('class="skill-name" itemprop="skills">','').replace('</','')          
            
            elif ("experienceRequirements" in x):
                xp += x.replace('</','')
                xp = xp[54:len(xp)]
        
        contrat = str(BeautifulSoup(raw_html, 'html.parser').find_all("dd"))
        contrat = contrat[6:len(contrat)].split('\n')[0]
                
        statut = str(BeautifulSoup(raw_html, 'html.parser').find_all("span", itemprop={"qualifications"}))
        statut = statut[33:len(statut)].replace("</span>]","")
        
        entreprise = str(BeautifulSoup(raw_html, 'html.parser').find_all('h4', attrs={"class":"t4 title"})[0:1]) 
        entreprise = entreprise[22:len(entreprise)].replace("</h4>]","").replace("\n","")
        
        partenaire = str(BeautifulSoup(raw_html, 'html.parser').find("a", {"id": "idLienPartenaire"}))
        try:
            idx=partenaire.index("href=")
            idP=partenaire.index("id=")
            partenaire = partenaire[idx:idP].replace('href="','').replace('"','')
        except:
            partenaire="Pas de lien"
            
        ref = str(BeautifulSoup(raw_html, 'html.parser').find_all("span", itemprop={"value"})[0:1])
        ref=ref[24:len(ref)].replace("</span>]","")
        
        """
        ajout des elems dans une liste 
        """
        liste.append(title) 
        liste.append(date)   
        liste.append(secteur)           
        liste.append(address)
        liste.append(description)
        liste.append(skills)
        liste.append(xp)
        liste.append(contrat)
        liste.append(statut)
        liste.append(entreprise)
        liste.append(partenaire)
        liste.append(ref)
        
        """
        ajout de chaque liste dans une autre liste ( double liste pour faire )
        """
        listeF.append(liste)
        c+=1
        print(c)
c=0
for i in listeF:
    """
    transformation de la liste en dictionnaire
    """
    date = str(datetime.datetime.now())  
    c += 1
    dico[date] = i
    
"""
transformation du dictionnaire en df avec les clés en index
"""


df= pd.DataFrame.from_dict(dico,orient=u'index',columns=[u"Intitule",u"Date",u"Secteur_Activite",u"Adresse",u"Description",u"Competences",u"Experience",u"Type_Contrat",u"Statut",u"Entreprise",u"Lien_Partenaire",u"Reference"])

print(df)

#
#from sqlalchemy import create_engine
#import argparse
#import os,configparser
#
#parser = argparse.ArgumentParser()
#parser.add_argument("-v", action="store_true", help="Verbose SQL")
#parser.add_argument("--base", help="Répertoire de movies")
#parser.add_argument("--bdd", help="Base de donnée")
#args = parser.parse_args()
#
#config = configparser.ConfigParser()
#config.read_file(open(os.path.expanduser("~/Téléchargements/.datalab.cnf")))
#
#base = args.base 
#
#DB="Job_Bot_Cyprien_Maxime?charset=utf8" 
#con = create_engine("mysql://%s:%s@%s/%s" % (config['myBDD']['user'], config['myBDD']['password'], config['myBDD']['host'], DB), echo=args.v)
#df.to_sql(con=con, name='PE_Scraping', if_exists='append')
