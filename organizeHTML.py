from bs4 import BeautifulSoup
from datetime import datetime


# Reading messages
data = "./data/messages.htm"
print("\nReading Messages from ", data)
with open(data, 'r') as f:
    html_doc = "".join(f.readlines())


print("\nFormating Messages..")
soup = BeautifulSoup(html_doc, 'html.parser')

"""
Get all message_headers which contain username

reversed them because the message is discending
"""
def get_messenge_user(message_header):
    # convert html to name and time
    name = message_header.contents[0].text
    time_str = message_header.contents[1].text
    time = datetime.strptime(time_str[:-7],"%A, %B %d, %Y at %I:%M%p")
    return (name, time)


message_headers = [get_messenge_user(name_time) for name_time in reversed(soup.find_all('div', class_="message_header"))]
# [(name, time), (name, time), ...]

message_contents = [p.text for p in reversed(soup.find_all('p'))]
# [message, message, ...]

print("Totally {} messages".format(len(message_headers)))