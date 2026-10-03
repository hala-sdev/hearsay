from hearsay.retrieval.wiki_passages import get_passages


r = get_passages('Albert Einstein')
for record in r[:10]:
    print(record['path'] + "  " +record['id'])



