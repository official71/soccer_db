# -*- coding: utf-8 -*-
import bs4
import urllib
import os
import re
from bs4 import BeautifulSoup
from collections import defaultdict

BASE_URL = "https://en.wikipedia.org"

def proc_teams(lst_teams):
    # for each team
    for team in lst_teams:
        url = BASE_URL + team['team_url']
        page = urllib.urlopen(url)
        soup = BeautifulSoup(page, 'lxml')
        
        # table class="infobox"
        tables = soup.findAll('table')
        for table in tables:
            if table.has_attr('class') and 'infobox' in table['class']:
                table_infobox = table
                break

        name = re.sub(r'[^a-z_]', '' ,re.sub(r' ', '_', team['name'].lower()))
        team['logo_image'] = "images/{}.png".format(name)
        # urllib.urlretrieve('https:'+table_infobox.img['src'], team['logo_image'])

        # year founded
        trs = table_infobox.findAll('tr')
        for tr in trs:
            th = tr.find('th')
            if th and re.match('Founded', th.text):
                try:
                    team['year'] = re.search(r'.*([1-2][0-9]{3}).*', th.find_next_sibling('td').text).group(1)
                except:
                    pass



def main():
    # url = BASE_URL + "wiki/2015-16_Premier_League/"
    url = "https://en.wikipedia.org/wiki/2015–16_Premier_League"
    page = urllib.urlopen(url)
    soup = BeautifulSoup(page, 'lxml')
    
    # find h3 with text 'Stadia'
    h3s = soup.findAll('h3')
    for h3 in h3s:
        if re.match(r'^Stadia', h3.text):
            h3_found = h3
            break

    # find the first table after h3_found
    elem = h3_found.next_sibling
    while elem:
        if elem.name == 'table':
            table = elem
            break
        elem = elem.next_sibling

    # traverse the table
    lst_teams = []
    tds = table.findAll('td')

    for r in xrange(len(tds) / 3):
        [c1, c2, c3] = [tds[i] for i in xrange(r*3 , (1+r)*3)]
        dd = {}
        dd['name'] = c1.text
        dd['team_url'] = c1.a['href']
        dd['arena'] = c2.text
        dd['arena_url'] = c2.a['href']
        # dd['capacity'] = c3.text
        lst_teams.append(dd)

    proc_teams(lst_teams)
    
    # print out the results
    print("id,name,logo,year,,,arena,url,arena_url")
    for (i, t) in zip(xrange(len(lst_teams)), lst_teams):
        # print("{},\"{}\",\"{}\",{},,,\"{}\",\"{}\",\"{}\"".format(i+1, t['name'], t['logo_image'], t['year'], t['arena'], t['team_url'], t['arena_url']))
        print("{},\"{}\",\"{}\",{},\"England\",,\"{}\"".format(i+1, t['name'], t['logo_image'], t['year'], t['arena']))




if __name__ == '__main__':
    main()