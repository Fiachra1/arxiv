import arxiv
import datetime
from openai import OpenAI
import smtplib

client = OpenAI()



# Construct the default API client.
arxiv_client = arxiv.Client()

# Search for the 10 most recent articles matching the keyword "quantum."
search = arxiv.Search(
    query="cat:cs.AI AND ti:lstm",
    max_results=100,
    sort_by=arxiv.SortCriterion.SubmittedDate,
)
results = arxiv_client.results(search)

# `results` is a generator; you can iterate over its elements one by one...
# for r in client.results(search):
#    if r.published.date() > datetime.date.today() + datetime.timedelta(days=-40):
#        print(r.title)
#        print(r.links[0])
#        print(r.summary)
# ...or exhaust it into a list. Careful: this is slow for large results sets.
all_results = list(results)
# print([r.title for r in all_results])
#
for a in range(3):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an ai researcher, skilled in explaining complex programming concepts for a general audience"},
                {"role": "user", "content": f"Summarise this abstract from the paper titled {all_results[a].title} in 3 main bullet points, keep the points short: {all_results[a].summary}"}
        ]
        )

    print(completion.choices[0].message)
