import json

if __name__ == "__main__":
    for n in ['music_singer_gpt.json', 'music_composition_gpt.json', 'music_instrument_gpt.json', 'music_song_gpt.json']:
        with open(n, 'r') as rf:
            data = json.load(rf)

        d = {}
        for k, w in data.items():
            d[k.lower()] = {}
            for id, s in w.items():
                d[k.lower()][id] = s

        with open(n, 'w') as wp:
            json.dump(d, wp, indent=4)
