'''
Script that generates a JSON file with the GPT-3 generated text. 
Steps:
1. Create an input file with the prompts (or prompt "entities") you'd like to run through GPT-3
2. Run this script ie python generate_gpt_json.py --prompts_file prompts.txt --output_file output.json --prompt_prefix "Give me a fun fact about "
3. The output file will contain the generated text from GPT-3, one entry for each leaf of the dictionary provided in step 1
'''

import openai
import json
import argparse
import time 
from tqdm import tqdm

openai.api_key = "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"

def generate(prompt, prompt_prefix, **kwargs):
    # sleep for 3 seconds to avoid rate-limiting
    time.sleep(3)
    prompt = prompt_prefix + prompt
    print(f"Generating output for {prompt}...")
    completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256, temperature=0.7,
                                          **kwargs)
    # get rid of the two newline characters that show up first
    return completion.choices[0]["text"][2:]


def generate_json_output(prompts_file, output_file, prompt_prefix=""):
    # read prompts from JSON file prompts_file
    with open(prompts_file, "r") as f:
        prompts = json.load(f)
    # generate output, but only for keys that are not dictionaries
    output = []
    # we can only do 20 requests per minute if we don't want to be rate-limited by OpenAI
    for key in tqdm(prompts):
        if isinstance(prompts[key], list):
            # loop through the list
            for key2 in tqdm(prompts[key]):
                output.append(generate(key2, prompt_prefix))
        else:
            output.append(generate(prompts[key], prompt_prefix))
    
    # write output to JSON file output_file
    with open(output_file, "w") as f:
        json.dump(output, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--prompt_prefix", type=str, default="")
    args = parser.parse_args()
    generate_json_output(args.prompts_file, args.output_file, prompt_prefix=args.prompt_prefix)