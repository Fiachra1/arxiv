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
    max_results=20,
    sort_by=arxiv.SortCriterion.SubmittedDate
)
results = arxiv_client.results(search)

all_results = list(results)

if len(all_results)>0:
    contents =[]
    j=0
    for i in range(len(all_results)):
        if all_results[i].published.date() >= datetime.date.today() + datetime.timedelta(days=-7):
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a quantum AI researcher, skilled in explaining complex programming concepts for a general audience"},
                    {"role": "user", "content": f"Using this format: 'Applicability to Quantum Deep Learning Research: ' Indicate whether the paper titled {all_results[i].title} th abstract {all_results[i].summary}\
                    has a High, Medium or Low applicability. Then summarise the paper in 3 main concise bullet points. Ensure everything is formatted nicely"}
                ]
                )
    
            contents.append('\n\n\n\nPaper Title: ' + all_results[i].title + ' \n Link to paper: ' + all_results[i].entry_id)
            contents.append('Arxiv Category: ' + all_results[i].primary_category)
            contents.append(completion.choices[0].message.content)
            print(f"Paper {i} titled {all_results[i].title} reviewed as it was published on {all_results[i].published.date()}")
            print(completion.choices[0].message.role)
            j += 1
        else:
            print(f"Paper not reviewed as it was published on {all_results[i].published.date()}")
    
    bullet_summaries = '\n\n'.join(contents)
    print(len(bullet_summaries))

    if len(contents) > 0:
        summary_data = bullet_summaries[:15000] if len(bullet_summaries) > 15000 else bullet_summaries
        summary_para = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an eloquent ai researcher, skilled in explaining complex concepts for a general audience"},
                {"role": "user", "content": f"The following text is a summarises multiple papers from arxiv: {summary_data} . Provide a brief summary of the general content investigated in the papers and the main paper I should focus on when considering research in quantum deep learning of time series data"}])
        
        message_to_send =(f'{j} Papers Reviewed Today \n\n\n\tSummary of Research Content\n\n'+summary_para.choices[0].message.content+'\n\n\n\n\tResearch papers:'+bullet_summaries)

        try:
            mail_msg(message_to_send)   
        except NameError:
            print("No mail today")
        else:
            print("You've got mail!")
else:
    print("No papers returned from Arxiv")

