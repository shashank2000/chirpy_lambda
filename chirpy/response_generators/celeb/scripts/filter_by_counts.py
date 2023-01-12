import json, tqdm

if __name__ == "__main__":
    all_celeb_info = json.load(open("../all_celeb_info.json"))
    filtered_celebs = {}

    for c in tqdm.tqdm(all_celeb_info):
        et_nums = 0
        new_celebs = {"pronoun": all_celeb_info[c]['pronoun'], "characters": []}
        sum_pg_views = 0
        for k in all_celeb_info[c]:
            if k != "pronoun":
                if k == "characters":
                    new_celebs[k] = []
                    # for ch in all_celeb_info[c][k]:
                    #     if "list of" not in ch[0].lower() and "film" not in ch[0].lower() and "tv" not in ch[0].lower():
                    #         new_celebs[k].append(ch)
                else:
                    new_celebs.update({k: []})
                    for e in all_celeb_info[c][k]:
                        if e[1] > 10000:
                            new_celebs[k].append(e)
                            et_nums += 1
                            if k == "songs":
                                sum_pg_views += e[1]
        new_celebs.update({'total_pg': sum_pg_views})
        if et_nums > 3:
            filtered_celebs.update({c: new_celebs})


    c_keys = list(filtered_celebs.keys())
    c_keys.sort(key=lambda x: filtered_celebs[x]['total_pg'], reverse=True)
    c_keys = c_keys[:150]
    sorted_celebs = {c: filtered_celebs[c] for c in c_keys}

    json.dump(sorted_celebs, open("150_song_celeb_info.json", "w+"))

    # json.dump(filtered_celebs, open("all_celeb_info.json", "w+"))

