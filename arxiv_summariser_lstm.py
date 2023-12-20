import arxiv
import datetime
from openai import OpenAI
import smtplib
import os
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def mail_msg(message):
    arxiv_pass = os.getenv("ARXIV_PASS")
    # creates SMTP session
    s = smtplib.SMTP("smtp.gmail.com", 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login("summaryarxiv@gmail.com", arxiv_pass)

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr(("Arxiv Summary", "summaryarxiv@gmail.com"))
    msg["To"] = formataddr(("Fiachra", "fiachra.merwick@gmail.com"))
    msg["Subject"] = "This weeks LSTM Papers"
    msg.attach(MIMEText(message, "html"))
    # sending the mail
    s.sendmail(msg["From"], msg["To"], msg.as_string())

    # terminating the session
    s.quit()


client = OpenAI()
# Construct the default API client.
arxiv_client = arxiv.Client()

# Search for the 10 most recent articles matching the keyword "quantum."
search = arxiv.Search(
    query="cat:cs.AI AND ti:lstm",
    max_results=20,
    sort_by=arxiv.SortCriterion.SubmittedDate,
)
results = arxiv_client.results(search)
all_results = list(results)
if len(all_results) > 0:
    contents = []
    j = 0
    for i in range(len(all_results)):
        if all_results[
            i
        ].published.date() >= datetime.date.today() + datetime.timedelta(days=-7):
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a quantum AI researcher, skilled in explaining complex programming concepts for a general audience",
                    },
                    {
                        "role": "user",
                        "content": f"Using this format: '<b>Applicability to Quantum Deep Learning of time-series Research: </b>' Indicate whether the paper titled {all_results[i].title} with abstract {all_results[i].summary}\
                    has a High, Medium or Low applicability. Add two empty lines using html <br> tags and then summarise the paper in 3 main concise bullet points, formatted using html unordered list items, under the heading '<b>Paper Summary: </b>'. Format everything using html tags so headings and bullet points render correctly in an html email",
                    },
                ],
            )

            contents.append(
                f"<br><br><br><br><b>Paper {j+1} Title:</b> "
                + all_results[i].title
                + " <br><b> Link to paper: </b>"
                + all_results[i].entry_id
            )
            contents.append(
                "<br><b>Primary Arxiv Category: </b>"
                + all_results[i].primary_category
                + "</b><br>"
            )
            contents.append(completion.choices[0].message.content)
            contents.append("<br><br><hr><br><br>")
            print(
                f"Paper {i} titled {all_results[i].title} reviewed as it was published on {all_results[i].published.date()}"
            )
            print(completion.choices[0].message.role)
            j += 1
        else:
            print(
                f"Paper not reviewed as it was published on {all_results[i].published.date()}"
            )

    bullet_summaries = "".join(contents)
    print(len(bullet_summaries))

    if len(contents) > 0:
        summary_data = (
            bullet_summaries[:15000]
            if len(bullet_summaries) > 15000
            else bullet_summaries
        )
        summary_para = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an eloquent ai researcher, skilled in explaining complex concepts for a general audience",
                },
                {
                    "role": "user",
                    "content": f"The following text summarises multiple papers from arxiv: {summary_data}. Provide a brief summary of the general content investigated in the papers and the main paper I should focus on when considering research in quantum deep learning of time series data",
                },
            ],
        )

        message_to_send = (
            f"<b>{j} Papers Reviewed Today</b> <br><br><br><b><u>Summary of Research Content</u></b><br><br>"
            + summary_para.choices[0].message.content
            + "<br><br><br><br><b><u>Research papers:</u></b>"
            + bullet_summaries
        )

        try:
            mail_msg(message_to_send)
        except NameError:
            print("No mail today")
        else:
            print("You've got mail!")
else:
    print("No papers returned from Arxiv")
