import collections
import json

import requests
from pprint import pprint
from bs4 import BeautifulSoup


def extract_lyrics(url, word_length=5):
    print(f"Fetching lyrics {url}...")
    r = requests.get(url)
    if r.status_code != 200:
        print("Page impossible a recuperer.")
        return []
    soup = BeautifulSoup(r.content, "html.parser")

    lyrics = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-1 kUgSbL")
    if not lyrics:
        return extract_lyrics(url)

    all_words = []
    for sentence in lyrics.stripped_strings:
        sentence_words = [word.strip(",").strip(".").lower() for word in sentence.split() if
                          len(word) > word_length and "[" not in word and "]" not in word]
        all_words.extend(sentence_words)

    return all_words


def get_all_urls():
    page_number = 1
    links = []
    while True:
        r = requests.get(f"https://genius.com/api/artists/29743/songs?page={page_number}&sort=popularity")
        if r.status_code == 200:
            print(f"Fetching page {page_number}")

            response = r.json().get("response", {})
            next_page = response.get("next_page")
            songs = response.get("songs")

            all_song_links = [song.get("url") for song in songs]
            links.extend(all_song_links)

            page_number += 1

            if not next_page:
                print("No more pages to fetch.")
                break
    return links


def get_all_words():
    urls = get_all_urls()
    words = []

    for url in urls:
        lyrics = extract_lyrics(url=url)
        words.extend(lyrics)

    counter = collections.Counter(words)
    most_common_words = counter.most_common(15)
    print(most_common_words)
    with open("data.json", "w") as f:
        json.dump(most_common_words, f, indent=4)


get_all_words()
