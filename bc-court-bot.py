#!/usr/bin/env python

# This is set on a schedule in ScraperWiki to run every hour

# Load in modules

import scraperwiki
import tweepy
import time
from datetime import datetime
import smtplib
import requests
from BeautifulSoup import BeautifulSoup

# Establish Twitter authorization.
# Need to sign up for API key at dev.twitter.com and connect your bot to a mobile phone so you can post through the API

TWEEPY_CONSUMER_KEY = 'YOUR_API_KEY'
TWEEPY_CONSUMER_SECRET = 'YOUR_API_KEY'
TWEEPY_ACCESS_TOKEN = 'YOUR_API_KEY'
TWEEPY_ACCESS_TOKEN_SECRET = 'YOUR_API_KEY'

# Setup initial record

record = {}
record["type"] = "Test"
record["citation"] = "This is a test record"
record["url"] =  "http://vancouversun.com/"
scraperwiki.sqlite.save(['url'], record)

auth1 = tweepy.auth.OAuthHandler(TWEEPY_CONSUMER_KEY, TWEEPY_CONSUMER_SECRET)
auth1.set_access_token(TWEEPY_ACCESS_TOKEN, TWEEPY_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth1)

def tweetit(record): # both decides to tweet and whether to add to table

    if len(record["citation"]) > 65:
        CitationText = record["citation"][:65] + "..."
    else:
        CitationText = record["citation"]
        
    query = "SELECT count(*) FROM swdata WHERE url = '" + record["url"] + "'"
    count = scraperwiki.sqlite.execute(query)
    countcheck = count['data'][0][0]
    if countcheck > 0:
        print "Already in database"
        print record
    if countcheck == 0:
        try:
            print "New record"
            scraperwiki.sqlite.save(['url'], record)
            statusupdate = "New ruling from the " + record["type"] + " in '" + CitationText + "' " + record["url"]
            print statusupdate
            api.update_status(statusupdate)
            time.sleep(30)
        except:
            print "Unable to add to table or tweet"
            
			
def scrape_bcsc(url): # in case page changes

    html = requests.get(url)
    htmlpage = html.content
    
    soup = BeautifulSoup(htmlpage)
    
    table = soup.find ("div", {"id" : "recentJudg"})

    decisions = table.findAll ("a")
    
    for decision in decisions:
        record = {}
        record["type"] = "B.C. Supreme Court"
        record["citation"] = decision.text
        record["url"] = 'http://www.courts.gov.bc.ca' + decision.get('href')
        tweetit(record)

def scrape_bcca(url):

    html = requests.get(url)
    htmlpage = html.content
    
    soup = BeautifulSoup(htmlpage)
    
    table = soup.find ("div", {"id" : "recentJudg"})

    decisions = table.findAll ("a", {"target" : "_blank"})
    
    for decision in decisions:
        record = {}
        record["type"] = "B.C. Court of Appeal"
        record["citation"] = decision.text
        record["url"] = 'http://www.courts.gov.bc.ca' + decision.get('href')
        tweetit(record)

def scrape_bcpc(url):
        html = requests.get(url)
        htmlpage = html.content
        
        soup = BeautifulSoup(htmlpage)
        
        table = soup.find ("div", {"class" : "view-content"})
    
        decisions = table.findAll ("a")
        
        for decision in decisions:
            record = {}
            record["type"] = "B.C. Provincial Court"
            record["citation"] = decision.text
            badurl = decision.get('href')
            record["url"] = badurl.replace("/judgments.php?link=","")
            tweetit(record)

try:
    scrape_bcsc("http://www.courts.gov.bc.ca/supreme_court/recent_Judgments.aspx")
except:
    print 'Difficulty scraping BCSC'
    
try:
    scrape_bcca("http://www.courts.gov.bc.ca/court_of_appeal/recent_Judgments.aspx")
except:
    print 'Difficulty scraping BCCA'
    
try:
    scrape_bcpc("http://www.provincialcourt.bc.ca/judgments-decisions")
except:
    print 'Difficulty scraping BCPC'
