import os

from flask import Flask, render_template, request
from dataclasses import dataclass
import requests
import json

app = Flask(__name__)


@dataclass
class Deleter:
    name: str
    id: str
    type: str


@dataclass
class DeleterSong:
    name: str
    id: str
    artistString: str
    deleted: bool
    reprinted: bool

def load_deleters(lang):
    deleters_clean = []
    deleters = json.loads(
        requests.get(
            f"https://vocadb.net/api/artists?tagId%5B%5D=7765&maxResults=1&getTotalCount=true&fields=256").text)
    total_count = deleters['totalCount']
    loop = [(i, 50) for i in list(range(0, total_count // 50))]
    if total_count % 50 != 0:
        loop.append((len(loop), total_count % 50))

    for off_mult, count in loop:
        deleters = json.loads(requests.get(
            f"https://vocadb.net/api/artists?start={50 * off_mult}&tagId%5B%5D=7765&maxResults={count}&lang={lang}").text)
        for deleter in deleters['items']:
            deleters_clean.append(Deleter(name=deleter['name'],
                                          id=deleter['id'],
                                          type=deleter['artistType']))
    return deleters_clean


@app.route('/')
def render_deleters():
    artistId = request.args.get('artistId')
    lang = request.cookies.get('nameLanguage')
    if lang is None:
        lang = 'Default'
    deleters_clean = load_deleters(lang)
    if artistId is None:
        artistId = deleters_clean[0].id
    else:
        artistId = int(artistId)

    songs = []
    deleter_songs = json.loads(requests.get(
        f"https://vocadb.net/api/songs?artistId%5B%5D={artistId}&maxResults=0&getTotalCount=true&artistParticipationStatus=OnlyMainAlbums").text)
    total_count = deleter_songs['totalCount']
    loop = [(i, 50) for i in list(range(0, total_count // 50))]
    if total_count % 50 != 0:
        loop.append((len(loop), total_count % 50))
    for off_mult, count in loop:
        deleter_songs = json.loads(requests.get(
            f"https://vocadb.net/api/songs?artistId%5B%5D={artistId}&start={50 * off_mult}&maxResults={count}&fields=PVs&artistParticipationStatus=OnlyMainAlbums&lang={lang}&sort=PublishDate").text)
        for song in deleter_songs['items']:
            if song['pvs'] and not any(deleter_song.id == song['id'] for deleter_song in songs):
                songs.append(DeleterSong(song['name'],
                                                     song['id'],
                                                     song['artistString'],
                                                     all(pv['disabled'] for pv in [orig for orig in song['pvs'] if
                                                                                   orig['pvType'] == 'Original']),
                                                     not all(pv['pvType'] == 'Original' for pv in song['pvs'])))

    return render_template('index.html', deleters=deleters_clean, artistId=artistId, songs=songs, lang=lang)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
