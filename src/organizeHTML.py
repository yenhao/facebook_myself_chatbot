from bs4 import BeautifulSoup
from datetime import datetime
import pickle

# Reading messages
data = "./data/messages.htm"
print("\nLoading Messages from ", data)
with open(data, 'r') as f:
    html_doc = "".join(f.readlines())


print("\nFormating HTML Messages..")
soup = BeautifulSoup(html_doc, 'html.parser')

owner_name = soup.title.text.split(' - ')[0]

print('\nYour Name is "' + owner_name +'"')

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

print('\nFinding Speakers and Messages')
message_headers = [get_messenge_user(name_time) for name_time in reversed(soup.find_all('div', class_="message_header"))]
# [(name, time), (name, time), ...]

message_contents = [p.text for p in reversed(soup.find_all('p'))]
# [message, message, ...]

print("\nTotally {} messages".format(len(message_headers)))

print("\nMapping Messages and Speaker..")
speaker_message_pair = list(zip(message_headers, message_contents))
# (('Huang Yen Hao', datetime.datetime(2014, 3, 2, 0, 20)), '部落格')

print("\nNow Mapping Dialogue!")

previous_speaker = ''
previous_time = ''
question = ''
answer = ''
qa_pair = []

for (speaker,time), message in speaker_message_pair:
    # print("\nSpeaker: {}, Message {}".format(speaker, message))
    if speaker != owner_name:
    #this is question
        if question != '' and previous_speaker != '' and answer != '':
            print("\nMatch Q - Speaker: {}, Message: {}".format(previous_speaker, question.strip()))
            print("      A - Speaker: {}, Message: {}".format(owner_name, answer.strip()))
            # append to qa_pair, set new question and speaker
            qa_pair.append(((previous_speaker,question.strip()),(owner_name,answer.strip())))
            previous_speaker = speaker
            question = message + ' '
            answer = ''
        else:
        # No question yet
            if speaker == previous_speaker:
            # same question, so append it on previous one
                question += message + ' '
            else:
            #set question and speaker
                previous_speaker = speaker
                question = message + ' '
                answer = ''
    else:
    #this is answer append longer
        answer += message + ' '

# dump to .py
print("Dump to .py")
with open("./data/qa.py", "w") as fp:
    fp.write("qa_pair = %s" % qa_pair)

# dump to pickle
print("Dump to pickle")
with open("./data/qa.pickle", "wb") as fp:
    pickle.dump(qa_pair, fp)

# Output if you want to see
print("Dump to txt")
with open('./data/qa.txt', 'w') as fp:
    out_text = ''
    for q,a in qa_pair:
        out_text += "{}\t{}\t{}\t{}\n".format(q[0],q[1],a[0],a[1])
    fp.write(out_text)

#
print('Build Q&A dictionary')
qa_dict = {q:a for (q_er,q),(a_er,a) in qa_pair}
np.save('conversationDictionary.npy',qa_dict)
