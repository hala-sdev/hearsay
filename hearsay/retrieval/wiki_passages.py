import wikipediaapi
from nltk.tokenize import sent_tokenize
import uuid
import nltk

nltk.download('punkt_tab')
wiki = wikipediaapi.Wikipedia(user_agent='hearsay (https://github.com/hala-sdev?tab=repositories)', language='en', extract_format=wikipediaapi.ExtractFormat.WIKI)
ignored_sections = ["See also", "References", "External links", "Further reading", "Notes"]
def wiki_search(title):
    site = wiki.page(title)
    def section_text(site, result, path):
        for section in site.sections:
            if section.title not in ignored_sections:
                data = section.text
                if data:
                    result.append({"article": title, "path": path + " > " + section.title, "text": data})
                section_text(section, result, path + " > " + section.title)
    result = [{"article": title, "path": title + " > Summary", "text": site.summary}]
    section_text(site, result, title)

    def remove_uncomlete_sent(chunk):
        sentences = chunk.split("\n")
        words = [len(sentence.split()) for sentence in sentences]
        avg = sum(words) / len(words) 
        return avg > 6


    result = [chunk for chunk in result if remove_uncomlete_sent(chunk["text"])]
    return result

def pack_sentences(sentences, max_words=250):
    packed = []
    Current = ""
    word_count = 0
    for s in sentences:
        if word_count + len(s.split()) > max_words:
            packed.append(Current)
            Current = s
            word_count = len(s.split())
        else:
            Current += " " + s
            word_count += len(s.split())
    packed.append(Current)
    cleaned = [p.strip() for p in packed if p.strip()]
    if len(cleaned) > 1 and len(cleaned[-1].split()) < 50:
        cleaned[-2] += " " + cleaned[-1]
        cleaned.pop()
    
    return cleaned

def get_passages(title, max_passages=20):
    wiki_results = wiki_search(title)
    if not wiki_results:
        print(f"No results found for title: {title}")
        return []
    passages = []
    for record in wiki_results:
        sentences = sent_tokenize(record["text"])
        packed_sentences = pack_sentences(sentences, max_words=250)
        for i, packed in enumerate(packed_sentences):
            passages.append({"article": record["article"], "path": record["path"], "text": packed, 'id': str(uuid.uuid5(uuid.NAMESPACE_URL, (record["path"] + ' > ' +f'{i}')))})

    return passages[:max_passages]
            