import json


def merge_opinions():
    celeb_opinion_file = open("../celeb_opinions.jsonl").readlines()
    merged_celeb_ops = {}
    for l in celeb_opinion_file:
        ld = json.loads(l)
        merged_celeb_ops.update(ld)
    return merged_celeb_ops


def merge_opinions_work(celeb_keys):
    celeb_keys = {c.lower(): c for c in celeb_keys}
    celeb_opinion_work_file = open("../celeb_opinions_work.jsonl").readlines()
    merged_celeb_work_ops = {}
    for l in celeb_opinion_work_file:
        ld = json.loads(l)
        if ld['work_name'] not in merged_celeb_work_ops:
            merged_celeb_work_ops.update({ld['work_name']: {}})
        if ld['celeb'] in celeb_keys:
            merged_celeb_work_ops[ld['work_name']].update({
                celeb_keys[ld['celeb']]: ld['opinion']
            })
    return merged_celeb_work_ops


def add_dummy_column():
    opinion_file = json.load(open("../individual_celeb_opinions.json"))
    for c in opinion_file:
        opinion_file[c] = {"opinion": opinion_file[c]}
    json.dump(opinion_file, open("../individual_celeb_opinions.json", "w+"))




if __name__ == "__main__":
    add_dummy_column()
    # merge_celeb_ops = merge_opinions()
    # json.dump(merge_celeb_ops, open("individual_celeb_opinions.json", "w+"))
    # merge_celeb_work_ops = merge_opinions_work(merge_celeb_ops)
    # json.dump(merge_celeb_work_ops, open("celeb_work_opinions.json", "w+"))

