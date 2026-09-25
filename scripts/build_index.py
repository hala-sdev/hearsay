import wikipediaapi
import nltk 

nltk.download('punkt_tab')
nltk.download('punkt')

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


wiki_results = wiki_search("Red Sea")
print(wiki_results)