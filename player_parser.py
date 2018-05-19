import datetime
import json
import re
import requests
import time
from dao import Dao
from lxml import html

DOMAIN = "https://www.transfermarkt.co.uk/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
NOW_DATE = datetime.datetime.today().strftime('%Y%m%d')
club_set = {}
country_set = {}

def parse_player_data(player_id):
    url  = DOMAIN + "player/profil/spieler/" + str(player_id)
    print(url)

    response = requests.get(url, headers = HEADERS)
    content = html.fromstring(response.text)

    # name
    nameBlock = content.xpath('//div[@class="dataName"]/h1')[0]
    fullName = nameBlock.text_content()
    nameBlock = nameBlock.xpath('b')[0]
    name = nameBlock.text_content()

    # full name
    dataBlock = content.xpath('//table[@class="auflistung"]')[0]
    tempTH = dataBlock[0].xpath('th')[0].text_content()
    if tempTH == "Name in home country:" or tempTH == "Complete name:":
        fullName = dataBlock[0].xpath('td')[0].text_content().strip()

    # birthday
    birthday = content.xpath('//span[@itemprop="birthDate"]')[0].text_content()
    birthday = birthday.split('(')[0].strip().replace(',', '')
    tempTime = time.mktime(time.strptime(birthday, '%b %d %Y'))
    birthday = time.strftime("%Y%m%d", time.gmtime(tempTime))

    # nationality
    nationality = content.xpath('//span[@class="dataValue"]/a[@class="vereinprofil_tooltip"]')
    if len(nationality) > 0:
        nationality = nationality[0].attrib['id']
        if int(nationality) not in country_set:
            nationality = get_national_id(nationality)
    else:
        nationality = "0"

    # position
    positionBlock = content.xpath('//div[@class="large-5 columns infos small-12"]/div[@class="auflistung"]/div')
    position = get_position_id(positionBlock[0].text_content().split(':')[1].strip())

    # height
    height = content.xpath('//span[@itemprop="height"]')[0].text_content().strip()
    height = re.sub("\D", "", height)
    height = int(height)

    # build player data
    param = (
        player_id, 
        fullName, name, birthday, nationality, position, height, 0, NOW_DATE, 
        fullName, name, birthday, nationality, position, height, NOW_DATE, 
    )
    Dao.upsert_player(param)

    print(fullName + ", " + name + ", " + birthday + ", " + nationality)

    # parse_market_data(player_id, response.text)

def parse_market_data(player_id, response):

    marketData = response.split("'Marktwert','data':")[1]
    marketData = marketData.split("}],'legend'")[0]
    marketData = marketData.replace("'", '"')

    tempClub = ''
    for data in marketData:
        club = data['marker']['symbol']
        if club != 'circle':
            club = club.split('/tiny/')[1]
            club = club.split('.')[0].split('_')[0]
            tempClub = club
        else:
            club = tempClub
        marketValue = str(data['y'])
        recrodDate = data['datum_mw'].replace(',', '')
        tempTime = time.mktime(time.strptime(recrodDate, '%b %d %Y'))
        recrodDate = time.strftime("%Y%m%d", time.gmtime(tempTime))

        param = (
            player_id, 
            club, recrodDate, marketValue, NOW_DATE, 
            club, recrodDate, marketValue, NOW_DATE, 
        )
        Dao.upsert_market(param)
        print(club + ", " + marketValue + ", " + recrodDate)

def parse_performance_data(player_id):
    url  = DOMAIN + "player/detaillierteleistungsdaten/spieler/" + str(player_id) + "/plus/1"
    print(url)

    response = requests.get(url, headers = HEADERS)
    content = html.fromstring(response.text)

    dataBlock = content.xpath('//div[@id="yw1"]/table[@class="items"]/tbody/tr')
    for row in dataBlock:
        td = row.xpath('td')
        season = td[0].text_content()
        club = row.xpath('td[4]/a')[0].attrib['id']
        appearance = td[4].text_content().replace("-", "0")
        goal = td[5].text_content().replace("-", "0")
        if len(td) > 15:
            assist = td[6].text_content().replace("-", "0")
            yellow = td[10].text_content().replace("-", "0")
            red = td[12].text_content().replace("-", "0")
            minute = re.sub("\D", "", td[15].text_content().replace("-", "0"))
        else:
            assist = '0'
            yellow = td[9].text_content().replace("-", "0")
            red = td[11].text_content().replace("-", "0")
            minute = re.sub("\D", "", td[14].text_content().replace("-", "0"))

        if club in club_set:
            param = (
                player_id, 
                season, club, appearance, goal, assist, yellow, red, minute, 
                season, club, appearance, goal, assist, yellow, red, minute
            )
            Dao.upsert_career(param)
            print(season + ", " + club + ", " + appearance + ", " + goal + ", " + assist + ", " + yellow + ", " + red + ", " + minute)

def parse_national_team_data(player_id):
    url  = DOMAIN + "player/nationalmannschaft/spieler/" + str(player_id)
    print(url)

    response = requests.get(url, headers = HEADERS)
    content = html.fromstring(response.text)

    dataBlock = content.xpath('//div[@class="large-8 columns"]/div[@class="box"][1]/table/tbody/tr')
    td = dataBlock[1].xpath('td')

    nationality = td[1].xpath('//span[@class="dataValue"]/a[@class="vereinprofil_tooltip"]')
    if (len(nationality)) > 0:
        nationality = nationality[0].attrib['id']

    if nationality in country_set:
        appearance = td[4].text_content().replace("-", "0")
        goal = td[5].text_content().replace("-", "0")
        debut_date = td[3].text_content().strip().replace(',', '')
        tempTime = time.mktime(time.strptime(debut_date, '%b %d %Y'))
        debut_date = time.strftime("%Y%m%d", time.gmtime(tempTime))
        debut_age = td[7].text_content().strip()

        param = (
            player_id, 
            nationality, appearance, goal, debut_date, debut_age, NOW_DATE, 
            nationality, appearance, goal, debut_date, debut_age, NOW_DATE
        )
        Dao.upsert_national_team(param)
        print(nationality + ", " + appearance + ", " + goal + ", " + debut_date + ", " + debut_age)

def build_club_set():
    result = Dao.get_all_club_id()
    global club_set
    club_set = { item['id'] for item in result }

def build_country_set():
    result = Dao.get_all_country_id()
    global country_set
    country_set = { item['id'] for item in result }

def get_position_id(position):
    return {
        'Keeper' : '1',
        'Left-Back' : '2',
        'Right-Back' : '3',
        'Sweeper' : '4',
        'Centre-Back' : '5',
        'Defensive Midfield' : '6',
        'Left Midfield' : '7',
        'Right Midfield' : '8',
        'Central Midfield' : '9',
        'Attacking Midfield' : '10',
        'Left Wing' : '11',
        'Right Wing' : '12',
        'Secondary Striker' : '13',
        'Centre-Forward': '14'
    }[position]

def get_national_id(nationality):
    return {
        '7658'  : '3439',   # BRAZIL U20
        '9323'  : '3377',   # FRANCE U21
        '3817'  : '3262',   # GERMANY U21
        '12609' : '3375',   # SPAIN U19
        '9567'  : '3375',   # SPAIN U21
        '16374' : '3300',   # PORTUGAL U21
        '22907' : '3299'    # ENGLAND U20
    }[nationality]

def get_all_player_by_team_id(team_id):
    url  = DOMAIN + "jumplist/startseite/verein/" + str(team_id)
    print(url)

    response = requests.get(url, headers = HEADERS)
    content = html.fromstring(response.text)

    player_list = []
    link = content.xpath('//table[@class="inline-table"]//tr[1]/td[2]/div[1]/span/a')
    for i in link:
        player_list.append(int(i.attrib['id']))

    return player_list

"""
Main
"""
Dao.init()
Dao.create_player_table()
Dao.create_career_table()
Dao.create_nation_table()
Dao.create_market_table()

build_club_set()
build_country_set()

"""
team_id :
    281 = Manchester City,     985 = Manchester United
    148 = Tottenham Hotspur
"""
player_list = get_all_player_by_team_id(148)
print(player_list)

for player_id in player_list:
    parse_player_data(player_id)
    parse_performance_data(player_id)
    # parse_national_team_data(player_id)
    time.sleep(1)