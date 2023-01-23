import pickle
import json
import time
import openai

openai.api_key = "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"


def generate(prompt, **kwargs):
    completion = None
    while completion is None:
        try:
            # create a completion
            completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256, temperature=0.7, **kwargs)
        except openai.error.ServiceUnavailableError:
            print('openai.error.ServiceUnavailableError')
            time.sleep(10)
        except openai.error.RateLimitError:
            print('openai.error.RateLimitError')
            time.sleep(10)
        except openai.error.OpenAIError:
            print('openai.error.OpenAIError')
            time.sleep(10)

    # print the completion
    return completion.choices[0].text

if __name__ == "__main__":

    # Generate GPT response

    # musical_instrument_lst = list(pickle.load(open("scraped_musical_instruments.p", "rb")))
    # gpt_response_for_musical_instrument = {}
    # num_samples = len(musical_instrument_lst)
    # for i, instr in enumerate(musical_instrument_lst):
    #     prompt = f"""Assume that your favorite instrument is the same with the user's.
    #             Generate a response that shows that you have a common interest and give a reason
    #             why you do so. Each reply should sounds like two best friends were talking.
    #             Your reply cannot be a question.
    #
    #             Chatbot: What is your favourite instrument?
    #             User: I like {instr}.
    #             Chatbot: """
    #     gpt_response = generate(prompt)
    #     gpt_response_for_musical_instrument[instr] = gpt_response
    #     if (i % 100 == 0):
    #         print(f'Completed {i} out of {num_samples}')
    #
    # with open('gpt_musical_instruments_1.json', 'w') as fp:
    #     json.dump(gpt_response_for_musical_instrument, fp, indent=4)

    # musical_work_lst = list(pickle.load(open("scraped_musical_work.p", "rb")))[:5000]
    # gpt_response_for_musical_work = {}
    # num_samples = len(musical_work_lst)
    # print('Starting')
    # for i, song in enumerate(musical_work_lst):
    #     prompt = f"""Show that you have heard of the song by including some detail about the
    #           song in the response. Your response must be true.
    #           Each reply should sounds like two best friends were talking.
    #
    #           Chatbot: What is your favourite song?
    #           User: I like {song}.
    #           Chatbot:"""
    #     gpt_response = generate(prompt)
    #     gpt_response_for_musical_work[song] = gpt_response
    #     if (i % 80 == 0):
    #         print(f'Completed {i} out of {num_samples}')
    #
    # with open('gpt_musical_work_1.json', 'w') as fp:
    #     json.dump(gpt_response_for_musical_work, fp, indent=4)

    # composition_lst = list(pickle.load(open("scraped_compositions.p", "rb")))
    # gpt_response_for_composition = {}
    # num_samples = len(composition_lst)
    # print('Starting')
    # for i, composition in enumerate(composition_lst):
    #     prompt = f"""Give a relatable, funny factoid in response to this conversation that will
    #             garner further good conversation, as if two best friends were talking. Each reply should
    #             include a thought-provoking statement that makes the conversant
    #             want to keep talking. Assume the user already knows what the composition is,
    #             but would like to learn obscure facts regarding its history, or popularity.
    #             Your factoid must be true.
    #
    #             Chatbot: What is your favourite composition you like to play?
    #             User: I like {composition}.
    #             Chatbot:"""
    #     gpt_response = generate(prompt)
    #     gpt_response_for_composition[composition] = gpt_response
    #     print(f'Completed {i} out of {num_samples}')
    #
    # with open('gpt_compositions.json', 'w') as fp:
    #     json.dump(gpt_response_for_composition, fp, indent=4)

    # singer_lst = list(pickle.load(open("scraped_singers.p", "rb")))[3000:]
    # gpt_response_for_singer = {}
    # num_samples = len(singer_lst)
    # print('Starting')
    # for i, singer in enumerate(singer_lst):
    #     prompt = f"""Name one of the popular songs of user's favorite singer, and
    #             tell the user why you like that song. Then ask the user if they have listened to it.
    #             Each reply should sounds like two best friends were talking.
    #             Your response must be true.
    #
    #             Chatbot: What is your favourite singer?
    #             User: I like {singer}.
    #             Chatbot:"""
    #     gpt_response = generate(prompt)
    #     gpt_response_for_singer[singer] = gpt_response
    #     print(f'Completed {i} out of {num_samples}')
    #
    # with open('gpt_singers_new_4.json', 'w') as fp:
    #     json.dump(gpt_response_for_singer, fp, indent=4)

    # musical_work_lst = list(pickle.load(open("scraped_musical_work.p", "rb")))
    # gpt_response_for_musical_work = {}
    # num_samples = len(musical_work_lst)
    # print('Starting')
    # for i, musical_work in enumerate(musical_work_lst):
    #     prompt = f"""Show that you have heard of the song by including some detail about the
    #             song in the response. Your response must be true.
    #             Each reply should sounds like two best friends were talking.
    #
    #             Chatbot: What is your favourite song?
    #             User: I like {musical_work}.
    #             Chatbot:"""
    #     gpt_response = generate(prompt)
    #     gpt_response_for_musical_work[musical_work] = gpt_response
    #     print(f'Completed {i} out of {num_samples}')
    #
    # with open('gpt_musical_work.json', 'w') as fp:
    #     json.dump(gpt_response_for_musical_work, fp, indent=4)

    # Generate GPT database

    # with open('gpt_singers.json', 'r') as rf:
    #     data = json.load(rf)
    #
    # d = {}
    # for k, v in data.items():
    #     d[k] = {"comment": v }
    # with open('music_singer_gpt.json', 'w') as wp:
    #     json.dump(d, wp, indent=4)

    pass