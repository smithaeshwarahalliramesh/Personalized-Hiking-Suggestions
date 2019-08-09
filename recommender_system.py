from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import time
import csv
import re

# Attribuutes of hikes
featuresList = ['backpacking', 'bird watching', 'camping', 'cross country skiing', 'fishing', 'hiking',
                'horseback riding', 'mountain biking', 'nature trips', 'off road driving', 'paddle sports',
                'road biking', 'rock climbing', 'scenic driving', 'skiing', 'snowshoeing', 'surfing',
                'trail running', 'walking', 'beach', 'cave', 'city walk', 'forest', 'historic site', 'hot springs',
                'lake', 'rocky', 'rails trails', 'river', 'views', 'waterfall', 'wild flowers', 'wildlife',
                'dog friendly', 'kid friendly', 'partially paved', 'stroller friendly', 'wheelchair friendly',
                'no shade', 'snow', 'no dogs', 'dogs on leash', 'bugs', 'over grown', 'scramble', 'washed out',
                'blowdown', 'muddy', 'bridge out', 'paved', 'off trail', 'closed']


def login():
    #driver.get(<trails website>)
    #email = driver.find_element_by_id("user_email").send_keys(<email>)
    #password = driver.find_element_by_id("user_password").send_keys(<password>)
    login_button = driver.find_element_by_class_name("login")
    login_button.click()


def get_best_trails_list(fileName):
    #driver.get("<trails website>/california")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'top-trails')))
    time.sleep(2)
    results = driver.find_element_by_class_name("top-trails")
    print(f'Found {results.text}')
    
    for i in range(0, 350):
        load_button = driver.find_element_by_class_name("trail-load")
        load_button.click()
        time.sleep(2)
    
    time.sleep(1)
    results = driver.find_element_by_xpath("//div[@data-react-class='SidebarTrailResultList']")
    
    with open(fileName, "w") as file:
        file.write(results.text)


def scrape_data_phase1():
    #path = <path to chrome driver>
    driver = webdriver.Chrome(path + str("chromedriver"))
    get_best_trails_list("trails_list_unformatted.text")


def format_data_phase1():
    with open("trails_list_unformatted.text", "r") as file:
        lines = file.readlines()

    with open("trails_data.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Index', 'Name', 'Difficulty', 'Number of reviews', 'Location'])
        
        for idx in range(0, len(lines)-1, 4): 
            index = lines[idx].split('\n')[0]
            name = lines[idx+1].split('\n')[0]
            info = re.split('[( )]', lines[idx+2])
            difficulty = info[0]
            
            if (len(info) > 1):
                reviews = info[1]
            else:
                reviews = 0
            
            location = lines[idx+3]
            writer.writerow([index, name, difficulty, reviews, location])


def get_data(file, i):
    stats = driver.find_element_by_id("trail-stats").text
    tags = driver.find_element_by_class_name("tag-cloud").text
    rating = driver.find_element_by_xpath("//meta[@itemprop='ratingValue']").get_attribute('content')
    driver.execute_script("window.history.go(-2)")
    time.sleep(2)
    file.write('\n')
    file.write(stats) 
    file.write('\n')
    file.write(tags)
    file.write('\n')
    file.write(rating)
    file.write('\n')


def scrape_data_phase2():
    with open("trails_info_unformatted.text", "a") as file:
        login()
        time.sleep(3)
        i = 0
        
        for trail in df['Name']:
            try:
                i += 1
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search")))
                search_bar = driver.find_element_by_id("search")
                search_bar.clear()
                time.sleep(1)
                search_bar.send_keys(trail)
                time.sleep(1)
                search_result = driver.find_element_by_class_name("algolia-hit")
                time.sleep(1)
                file.write(search_result.text)
                search_result.click()
                time.sleep(1)
                expand = driver.find_element_by_class_name("expand")
                time.sleep(1)
                expand.click()
                time.sleep(2)
                get_data(file, i)
            except:
                print(trail)
                error = driver.find_element_by_tag_name('h1')
                
                if (error.text == "504 Gateway Time-out"):
                    print("timeout")
                    time.sleep(1)
                    driver.refresh()
                    time.sleep(2)
                    get_data(file, i)
                
                continue


def format_data_phase2():
    with open("trails_info_unformatted.text", "r") as file:
        trailInfo = file.read().split('\n')

    trailsData = pd.read_csv('trails_data.csv', index_col=0)
    trailsData['Distance'] = None
    trailsData['Elevation Gain'] = None
    trailsData['Route Type'] = None
    trailsData['Features'] = None
    trailsData['Rating'] = None

    rows, cols = trailsData.shape
    nameList = trailsData['Name']

    for i in range(rows):
        if nameList[i] in trailInfo:
            idx = trailInfo.index(nameList[i])
            trailsData['Distance'][i] = trailInfo[idx+3]
            trailsData['Elevation Gain'][i] = trailInfo[idx+5]
            trailsData['Route Type'][i] = trailInfo[idx+7]
            trailsData['Features'][i] = trailInfo[idx+8]
            trailsData['Rating'][i] = trailInfo[idx+9]

    trailsData.dropna(inplace=True)
    trailsData.reset_index(drop=True, inplace=True)

    trailsData.to_csv("trail_info.csv")


def cleanData():
    trailsInfo = pd.read_csv("trail_info.csv", index_col=0)
    trailsInfo = trailsInfo[['Name', 'Location', 'Difficulty', 'Number of reviews', 'Distance', 'Elevation Gain', 'Route Type', 'Rating', 'Features']]
    
    difficulty = {'EASY': 1, 'MODERATE': 2, 'HARD': 3}
    trailsInfo.Difficulty = [difficulty[entry] for entry in trailsInfo.Difficulty] 
    
    trailsInfo['Distance'] = trailsInfo['Distance'].map(lambda x: x.split(" ")[0])
    trailsInfo['Elevation Gain'] = trailsInfo['Elevation Gain'].map(lambda x: x.split(" ")[0])
    trailsInfo['Location'] = trailsInfo['Location'].map(lambda x: x.split("\n")[0])
    trailsInfo['Elevation Gain'] = trailsInfo['Elevation Gain'].map(lambda x: x.replace(",", ""))
    trailsInfo.rename(columns={'Distance': 'Distance in miles', 'Elevation Gain': 'Elevation Gain in feet'}, inplace=True)
    
    routeType = {'Out & Back': 1, 'Loop': 2, 'Point to Point': 3}
    trailsInfo['Route Type'] = [routeType[entry] for entry in trailsInfo['Route Type']]         
    
    for feature in featuresList:
        trailsInfo[feature] = 0
    trailsInfo['Features'] = trailsInfo['Features'] + " "
    
    for idx, features in enumerate(trailsInfo['Features']):
        attrList = features.split(", ")[:-1]
        
        for attr in attrList:
            trailsInfo[attr].iloc[idx] = 1
    
    trailsInfo.drop(columns=["Features"], inplace=True)
    
    trailsInfo.to_csv("trail_info_cleaned.csv")


def getHikeList():
    df = pd.read_csv("trail_info_cleaned.csv", index_col=1)
    return list(df.index)


def recommendHike(df, hike, n):
    similarity = cosine_similarity(hike, df)
    idx = np.argsort(similarity)[0]
    recIdx = idx[-2:-n-2:-1]
    recList = [df.index[i] for i in recIdx]
    return recList


def recommendPopularHikes(df, n):
    df.sort_values(by=['Rating'], inplace=True, ascending=False)
    recList = [df.index[i] for i in range(n)]
    return recList


def recommendation(hikeName):
    trailsInfo = pd.read_csv("trail_info_cleaned.csv", index_col=1)
    trailsInfo.drop(columns=['Unnamed: 0', 'Location'], inplace=True)
    trailsInfo['Elevation Gain in feet'] = trailsInfo['Elevation Gain in feet'].map(lambda x: x.replace(",", ""))
    if hikeName in trailsInfo.index:
        return recommendHike(trailsInfo, trailsInfo.loc[[hikeName]], 10)
    return recommendPopularHikes(trailsInfo, 10)
