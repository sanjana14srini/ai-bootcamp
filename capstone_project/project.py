import os
import sys




# setting up the arxiv api
import urllib, urllib.request
import feedparser


def get_data(paper_name="electron", max_results=2):

    paper_name = paper_name.replace(" ", "&")

    url = f'http://export.arxiv.org/api/query?search_query=all:{paper_name}&max_results={max_results}'
    data = urllib.request.urlopen(url).read()
    feed = feedparser.parse(data)


    return feed



def extract_data(feed):
    doc = []
    
    for entry in feed.entries:
        entry_dict = { 
            "id": entry.id,
            "title": entry.title,
            "authors": entry.authors,
            "published": entry.published,
            "abstract": entry.summary,

        }
        doc.append(entry_dict)

    return doc



feed = get_data("LORA", 10)
doc = extract_data(feed)

print(doc)