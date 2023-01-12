import time

import openai
import json
import pickle
import tqdm

openai.api_key = "<REPLACE WITH KEY>"


def generate(prompt, **kwargs):
    # create a completion
    completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256, temperature=0.7, **kwargs)

    # print the completion
    return completion.choices[0].text


def create_prompts(celeb_info, list_celebs=[]):
    all_p = []

    MOVIE_TV_PROMPT = "Give a relatable opinion about {name}'s performance in {film_tv}."
    SONG_PROMPT = "Give a relatable opinion about {name}'s song {song}."

    for ce in celeb_info:
        for k in celeb_info[ce]:
            if k not in ['pronoun', 'total_pg', 'films', 'tv', 'characters']:
                for w in celeb_info[ce][k]:
                    if w[1] > 10000:
                        p_dict = {"celeb": ce}
                        p_dict.update({"work_name": w[0]})
                        if k in ["films", "tv"]:
                            p_dict.update({"prompt": MOVIE_TV_PROMPT.format(name=ce, film_tv=w[0])})
                        else:
                            p_dict.update({"prompt": SONG_PROMPT.format(name=ce, song=w[0])})
                        all_p.append(p_dict)
    return all_p


GENERATION_PROMPT = "Give a relatable opinion about {name}."


if __name__ == "__main__":
    # all_celebs = json.load(open("filtered_celeb.json"))
    sub_celebs = ["Shawn Mendes", "Olivia Rodrigo", "Shakira", "Rihanna", "The Weeknd", "Keanu Reeves",
                  "Rachel McAdams", "Jude Law", "James McAvoy", "Michael Fassbender", "Jesse Eisenberg", "Adam Levine"]
    all_celebs = pickle.load(open("../list_celebs.p", "rb"))
    all_celeb_info = json.load(open("../all_celeb_info.json"))

    all_prompts = create_prompts(all_celeb_info)
    print(all_prompts[:5])
    err_cts = 0

    cts = 0
    while cts < len(all_prompts):
        celeb_opinion_file = open("../celeb_opinions_work.jsonl", "a+")
        try:
            for p in tqdm.tqdm(all_prompts[cts:]):
                output = generate(p['prompt'])
                output = output.replace("\n", "")
                print(output)
                p.update({"opinion": output})
                cts += 1
                celeb_opinion_file.write(json.dumps(p) + "\n")
                time.sleep(5)
        except openai.error.ServiceUnavailableError:
            celeb_opinion_file.close()
            err_cts += 1
            time.sleep(20 + 10 * err_cts)
        except openai.error.RateLimitError:
            celeb_opinion_file.close()
            err_cts += 1
            time.sleep(20 + 10 * err_cts)
        except openai.error.OpenAIError:
            celeb_opinion_file.close()
            err_cts += 1
            time.sleep(20 + 10 * err_cts)
        celeb_opinion_file.close()

