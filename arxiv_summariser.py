import arxiv
import datetime
from openai import OpenAI
import smtplib
import os

def mail_msg(message):
    arxiv_pass = os.getenv('ARXIV_PASS')
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
     
    # start TLS for security
    s.starttls()
     
    # Authentication
    s.login("summaryarxiv@gmail.com", arxiv_pass)
     
    message_cw_sub = f"Subject: This weeks Quantum Papers\n\n{message}"
    # sending the mail
    s.sendmail("summaryarxiv@gmail.com", "fiachra.merwick@gmail.com", message_cw_sub)
     
    # terminating the session
    s.quit()
    
client = OpenAI()

# Construct the default API client.
arxiv_client = arxiv.Client()

# Search for the 10 most recent articles matching the keyword "quantum."
search = arxiv.Search(
    query="cat:cs.AI AND ti:quantum",
    max_results=100,
    sort_by=arxiv.SortCriterion.SubmittedDate,
)
results = arxiv_client.results(search)

all_results = list(results)

contents =[]
for i in range(len(all_results)):
    if all_results[i].published.date() > datetime.date.today() + datetime.timedelta(days=-7):
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an ai researcher, skilled in explaining complex programming concepts for a general audience"},
                    {"role": "user", "content": f"Summarise this abstract from the paper titled {all_results[i].title} in 3 main bullet points, keep the points concise and before the bullet points state whether the paper has a High, Medium or Low applicability to Quantum Deep Learning research in time-series analysis, then add two empty lines: {all_results[i].summary}"}
            ]
            )

        contents.append(all_results[i].title + ' : ' + all_results[i].entry_id)
        contents.append(all_results[i].primary_category)
        contents.append(completion.choices[0].message.content)

mail_msg('\n\n'.join(contents))
