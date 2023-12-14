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
     
    message_cw_sub = f"Subject: Todays Quantum Papers\n\n{message}"
    # sending the mail
    s.sendmail("summaryarxiv@gmail.com", "fiachra.merwick@gmail.com", message)
     
    # terminating the session
    s.quit()
