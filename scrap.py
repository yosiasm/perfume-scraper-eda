import requests
from bs4 import BeautifulSoup as bs
from fake_headers import Headers
import cloudscraper

import requests
from collections import OrderedDict
import warnings

warnings.filterwarnings("ignore")


# from collections import OrderedDict
# proxies = {'https': 'socks5://localhost:9050','http': 'socks5://localhost:9050'}
# s = requests.session()
# s.proxies.update(proxies)
# headers = OrderedDict([('User-Agent',
#               'ScraperBot/1.0'),
#             #   'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.1502.79 Mobile Safari/537.36'),
#              ('Accept',
#               'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'),
#              ('Accept-Language', 'en-US,en;q=0.9'),
#              ('Accept-Encoding', 'gzip, deflate')])


scraper = cloudscraper.create_scraper(
    delay=10,
    browser={
        "custom": "ScraperBot/1.0",
    },
)
# scraper = cloudscraper.create_scraper(
#     # sess=s,
#     delay=10,
#     browser={
#         "Mozilla/5.0": "(Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0",
#     },
# )
# scraper.headers
# 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0'

import json
import pandas as pd

with open("perfumes.json", "r") as r:
    df_perfumes_sample = json.load(r)
df_perfumes_sample = pd.DataFrame(df_perfumes_sample)
df_perfumes_sample

import os
import re
import time
import random

list_perf = os.listdir("perfumes")
for y in [2023 - i for i in range(100)]:
    counter = 0
    print(y)
    time.sleep(15)
    for idx, row in (
        df_perfumes_sample[df_perfumes_sample.year == y].head(20).iterrows()
    ):
        filename = row.href.strip("/perfume/").strip(".html").replace("/", "_")
        if filename + ".json" in list_perf:
            counter += 1
            print(filename, "exists")
            continue
        try:
            perf_url = f"https://www.fragrantica.com{row.href}?"
            print(perf_url)
            perfume_html = scraper.get(perf_url)
            soup_perf = bs(perfume_html.content)

            # print('pyramid',perf_url)
            pyramid = soup_perf.find_all("div", {"id": "pyramid"})[0].text
            pyramid = (
                pyramid.replace(" Notes", "-notes")
                .strip("Perfume Pyramid")
                .strip("Vote for Ingredients")
            )
            pyramid = re.findall("[A-Z][^A-Z]*", pyramid)
            pyramid_map = {}
            key = pyramid[0]
            for item in pyramid:
                if "-notes" in item:
                    key = item
                    continue
                if key not in pyramid_map:
                    pyramid_map[key] = []
                item = item.replace("\n", "")
                pyramid_map[key].append(item)
            # pyramid_map

            # print('accords')
            accords = soup_perf.find_all("div", {"class": "accord-bar"})
            accords_detail = [
                {
                    "width": acc["style"]
                    .strip(";")
                    .split(";")[-1]
                    .strip("width: ")
                    .strip("%"),
                    "opacity": acc["style"]
                    .strip(";")
                    .split(";")[-1]
                    .strip("opacity: ")
                    .strip("%"),
                    "text": acc.text,
                }
                for acc in accords
            ]
            # accords_detail

            # print('reviews')
            reviews = soup_perf.find_all("div", {"itemprop": "reviewBody"})
            reviews = [rev.text for rev in reviews][:20]
            # reviews

            doc = {
                "href": row.href,
                "year": row.year,
                "review_clean": row.review_clean,
                "pyramid": pyramid_map,
                "accords_detail": accords_detail,
                "reviews": reviews,
            }
            filename = row.href.strip("/perfume/").strip(".html").replace("/", "_")
            with open(f"perfumes/{filename}.json", "w") as w:
                json.dump(doc, w)
        except Exception as e:
            print(e)
            # import sys

            # sys.exit()
            # print(scraper.get("http://checkip.amazonaws.com/").content)
            time.sleep(12 * 60)
        time.sleep(random.random())
        if random.random() > 0.7:
            time.sleep(2)
        print("sleeping")
        time.sleep(11 + random.random())
        scraper.get("https://www.fragrantica.com")
        counter += 1
        print(counter, "/", len(df_perfumes_sample), row.href)
