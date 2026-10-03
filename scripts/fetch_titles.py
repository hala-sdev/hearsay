import json
import wikipediaapi

wiki = wikipediaapi.Wikipedia(user_agent='hearsay (https://github.com/hala-sdev?tab=repositories)', language='en', extract_format=wikipediaapi.ExtractFormat.WIKI)
def get_titles(sublist):
    prefix =['Template talk:', 'Wikipedia:', 'Category:', 'Template:', 'User:']
    page = wiki.page(f"Wikipedia:Vital articles/Level/4/{sublist}")
    links = page.links
    titles = []
    for title in links.keys():
        if not any(title.startswith(p) for p in prefix):
            titles.append(title)
    return titles

sections = ["Mathematics", "People", "History", "Geography", "Arts", "Philosophy and religion", "Everyday life", "Biological and health sciences", "Society and social sciences", "Physical sciences", "Technology"] 
all_titles = []
title_sections = {}
for s in sections:
    titles = get_titles(s)
    title_sections[s] = []
    for t in titles:
        if t not in all_titles:
            all_titles.append(t)
            title_sections[s].append(t)

with open("data/titles.json", "w", encoding="utf-8") as f:
   json.dump(title_sections, f, indent=2, ensure_ascii=False)
print(f"Total number of unique titles: {len(all_titles)}")