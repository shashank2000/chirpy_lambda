import json

if __name__ == "__main__":
    celeb_opinion_file = json.load(open("../individual_celeb_opinions.json"))
    all_celeb_info = json.load(open("../reverse_filtered_celeb.json"))
    missing_celebs = {}
    all_exist_celeb = [c.lower() for c in celeb_opinion_file]
    for c in all_celeb_info:
        if c not in all_exist_celeb:
            missing_celebs.update({
                c: all_celeb_info[c]
            })
    json.dump(missing_celebs, open("../missing_celebs.json", "w+"))
