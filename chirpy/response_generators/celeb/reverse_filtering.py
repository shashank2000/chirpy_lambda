import json
import pickle


if __name__ == "__main__":
    list_celebs = pickle.load(open("list_celebs.p", "rb"))
    list_celebs.sort(key=lambda x: x[1], reverse=True)
    filtered_celebs = json.load(open("filtered_celebs.json"))
    reverse_celeb = {}
    for c in list_celebs:
        c_key = c[0].lower()
        if c_key in filtered_celebs:
            reverse_celeb.update({
                c_key: filtered_celebs[c_key]
            })
    json.dump(reverse_celeb, open("reverse_filtered_celeb.json", "w+"))