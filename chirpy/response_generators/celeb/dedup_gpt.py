import json

if __name__ == "__main__":
    all_celeb_names = open("gpt_celebs_2021_300.txt").readlines()
    all_celeb_names = [x.split(". ")[1].replace("\n", "") for x in all_celeb_names]
    all_celeb_names = set(all_celeb_names)
    total_celeb = {}
    print("Deduplicated Celeb Length:", len(all_celeb_names))
    for c in all_celeb_names:
        total_celeb.update({c: {"movies": [], "songs": [], "tv shows": []}})
    json.dump(total_celeb, open("all_celeb_scraped.json", "w+"))