import json
import random

def get_pages(row):
    titles = set()
    for evd in row["evidence"]:
        for title in evd:
            if title[2] is not None:
                titles.add(fever_to_title(title[2]))
    return sorted(titles)
 
def make_record(row, group):
    record = {"id": row['id'], "group":group, "label": row["label"], "claim": row["claim"], "pages": get_pages(row), "matched": row.get("matched", [])}
    return record


def fever_to_title(page):
    return page.replace("_", " ").replace("-LRB-", "(").replace("-RRB-", ")").replace("-COLON-", ":").replace("-LSB-", "[").replace("-RSB-", "]").replace("-LCB-", "{").replace("-RCB-", "}")

def subject_match(claim, title):
    for prefix in [title, "The " + title]:
        if claim.startswith(prefix):
            rest = claim[len(prefix):]
            if len(rest) >= 2 and rest[0] == " " and rest[1].islower():
                return True 

    return False


supports = []
refutes = []
nei_a = []
nei_b = []

with open("data/titles.json", encoding="utf-8") as f:
    data = json.load(f)
    titles = set()
    long_titles = set()
    for title in data.values():
        titles.update(title)
    for t in titles:
        if len(t.split()) >= 2:
            long_titles.add(t)


with open("data/shared_task_dev.jsonl", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)

        if row["label"] == "NOT ENOUGH INFO":
            matched = []
            for t in long_titles:
                if subject_match(row["claim"], t):
                    matched.append(t)
            row["matched"] = matched
            if matched:                       
                row["group"] = "NEI-A"
                nei_a.append(row)

            else:
                row["group"] = "NEI-B"
                nei_b.append(row)


            continue

        for evd in row["evidence"]:
            pages = []
            for title in evd:
                pages.append(fever_to_title(title[2]))
            if all(p in titles for p in pages):
                if row["label"] == "SUPPORTS":
                    row['group'] = "SUPPORTS"
                    supports.append(row)
                elif row["label"] == "REFUTES":
                    row['group'] = "REFUTES"
                    refutes.append(row)
                break

random.seed(42)
support_list = random.sample(supports, 34)
refutes_list = random.sample(refutes, 34)
nei_a_list = random.sample(nei_a, 34)
nei_b_list = random.sample(nei_b, 20)
retrieval_set = supports + refutes
full_list = support_list + refutes_list + nei_a_list + nei_b_list


with open("eval/fever_sample.jsonl", "w", encoding="utf-8") as f:
    for row in full_list:
        group = row["group"]
        record = make_record(row, group)
        record_clean = json.dumps(record, ensure_ascii=False) + "\n"
        f.write(record_clean)

with open("eval/fever_retrieval.jsonl", "w", encoding="utf-8") as f:
    for row in retrieval_set:
        group = row["group"]
        record = make_record(row, group)
        record_clean = json.dumps(record, ensure_ascii=False) + "\n"
        f.write(record_clean)


print(len(retrieval_set))

