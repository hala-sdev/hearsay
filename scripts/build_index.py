import wikipediaapi
from nltk.tokenize import sent_tokenize

wiki = wikipediaapi.Wikipedia(user_agent='hearsay (https://github.com/hala-sdev?tab=repositories)', language='en', extract_format=wikipediaapi.ExtractFormat.WIKI)

ignored_sections = ["See also", "References", "External links", "Further reading", "Notes"]
def wiki_search(title):
    site = wiki.page(title)
    def section_text(site, result):
        for section in site.sections:
            if section.title not in ignored_sections:
                data = section.text
                if data:
                    result.append(data)
                section_text(section, result)
    result = [site.summary]
    section_text(site, result)

    def remove_uncomlete_sent(chunk):
        sentences = chunk.split("\n")
        words = [len(sentence.split()) for sentence in sentences]
        avg = sum(words) / len(words) 
        return avg > 6


    result = [chunk for chunk in result if remove_uncomlete_sent(chunk)]
    return result

def pack_sentences(sentences, max_words=250, max_passages=20):
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
    return [p.strip() for p in packed if p.strip()]

def get_passages(title):
    wiki_results = wiki_search(title)
    if not wiki_results:
        print(f"No results found for title: {title}")
        return []
    passages = []
    for chunk in wiki_results:
        sentences = sent_tokenize(chunk)
        packed_sentences = pack_sentences(sentences, max_words=250, max_passages=20)
        passages.extend(packed_sentences)
    num_passages = len(passages)
    sum_words = sum(len(s.split()) for s in passages)
    largest = max(len(s.split()) for s in passages)
    print(f"Title: {title}")
    print(f"Number of passages: {num_passages}")
    print(f"Total number of words: {sum_words}")
    print(f"Largest passage word count: {largest}\n\n")
    return passages[:20]


passa = get_passages("France")
passb = get_passages("Albert Einstein")
passc = get_passages("Photosynthesis")
passd = get_passages("make it boy")




