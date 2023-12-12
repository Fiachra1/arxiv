import arxiv
import datetime

# Construct the default API client.
client = arxiv.Client()

# Search for the 10 most recent articles matching the keyword "quantum."
search = arxiv.Search(
    query="cat:cs.AI AND ti:lstm",
    max_results=100,
    sort_by=arxiv.SortCriterion.SubmittedDate,
)
results = client.results(search)

# `results` is a generator; you can iterate over its elements one by one...
for r in client.results(search):
    if r.published.date() > datetime.date.today() + datetime.timedelta(days=-40):
        print(r.title)
        print(r.links[0])
        print(r.summary)
# ...or exhaust it into a list. Careful: this is slow for large results sets.
# all_results = list(results)
# print([r.title for r in all_results])
