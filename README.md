# facebook_myself_chatbot

This work is reference from [this repo](https://github.com/adeshpande3/Facebook-Messenger-Bot), in this work, we modify it to be able to work on python3 and 中文(Chinese) user.


### How to download all your data from Facebook?

Go to Facebook [setting page](https://www.facebook.com/settings), check **Download a copy** of your Facebook data to download all your Facebook data.

After a while, Facebook will finish archive your data, you are able to downlaod it.

The downlaoded file would be a html-like webpage files, go to html folder and copy the **message.htm** file to `./data/message.htm`

**NOTICE** all the command above and below is in inside the `src` folder ^^

### Preprocess Data to Q&A type

We'll need the following libruary to excute this program
```
bs4
numpy
pickle
```

Excute `python3 organizeHTML.py` will help you to build 

1. **qa.pickle**, which is a list of Q&A pair.

`[((question_user, question),(answer_user, answer)), ...]`

2. **conversationDictionary.npy**, which is a dictionary for Q&A pair

`{ question:answer , ...}`

### Train Seq2seq Model

We'll need the following libruary to excute this program
```
tensorflow
numpy
sklearn
pickle
jieba
```
Excute `python3 seq2seq.py` to train your model!
