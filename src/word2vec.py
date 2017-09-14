import tensorflow as tf 
import numpy as np 
import re
from collections import Counter
import sys
import math
from random import randint
import pickle
import os
import jieba
import multiprocessing as mp

wordVecDimensions = 300
batchSize = 128
numNegativeSample = 64
windowSize = 5
numIterations = 100000


# This function just takes in the conversation data and makes it 
# into one huge string, and then uses a Counter to identify words
# and the number of occurences
def processDataset(qa_pickle):
    with open(qa_pickle, "rb") as fp:
        qa_pair = pickle.load(fp)
    sentence = ""
    for q,a in qa_pair:
        sentence += q[1] + a[1]
    finalDict = Counter(jieba.cut(sentence, cut_all=False))
    return sentence, finalDict

def buildXYTrain(allUniqueWords, allWords, windowSize, i):
    if i % 1000 == 0:
        print('Finished %d/%d total words' % (i, len(allWords)))
    xTrain=[]
    yTrain=[]
    wordsAfter = allWords[i + 1:i + windowSize + 1]
    wordsBefore = allWords[max(0, i - windowSize):i]
    wordsAdded = wordsAfter + wordsBefore
    for word in wordsAdded:
        xTrain.append(allUniqueWords.index(allWords[i]))
        yTrain.append(allUniqueWords.index(word))
    return (xTrain, yTrain)


def createTrainingMatrices(dictionary, corpus):
    allUniqueWords = list(dictionary)
    allWords = list(jieba.cut(corpus, cut_all=False))
    numTotalWords = len(allWords)
    xTrain=[]
    yTrain=[]

    for i in range(numTotalWords):
        if i % 1000 == 0:
            print('Finished %d/%d total words' % (i, numTotalWords))
        wordsAfter = allWords[i + 1:i + windowSize + 1]
        wordsBefore = allWords[max(0, i - windowSize):i]
        wordsAdded = wordsAfter + wordsBefore
        for word in wordsAdded:
            xTrain.append(allUniqueWords.index(allWords[i]))
            yTrain.append(allUniqueWords.index(word))

    # multi process mode 
    # print("Using {} core to build training data".format(mp.cpu_count()))
    # pool = mp.Pool(processes=mp.cpu_count()) 
    # multiple_results = [pool.apply_async(buildXYTrain, (allUniqueWords, allWords, windowSize, i,)) for i in range(numTotalWords)]
    # for i, xTr, yTr in enumerate([res.get() for res in multiple_results]):
    #     xTrain += xTr
    #     yTrain += yTr

    return allUniqueWords, xTrain, yTrain

def getTrainingBatch():
    num = randint(0,numTrainingExamples - batchSize - 1)
    arr = xTrain[num:num + batchSize]
    labels = yTrain[num:num + batchSize]
    return arr, labels[:,np.newaxis]

if __name__ == '__main__':
    
    
    # Loading the data structures if they are present in the directory
    if (os.path.isfile('Word2VecXTrain.npy') and os.path.isfile('Word2VecYTrain.npy') and os.path.isfile('wordList.txt')):
        xTrain = np.load('Word2VecXTrain.npy')
        yTrain = np.load('Word2VecYTrain.npy')
        print('Finished loading training matrices')
        with open("wordList.txt", "rb") as fp:
            wordList = pickle.load(fp)
        print('Finished loading word list')

    else:
        fullCorpus, datasetDictionary = processDataset('./data/qa.pickle')
        print('Finished parsing and cleaning dataset')
        wordList, xTrain, yTrain  = createTrainingMatrices(datasetDictionary, fullCorpus)
        print('Finished creating training matrices')
        np.save('Word2VecXTrain.npy', xTrain)
        np.save('Word2VecYTrain.npy', yTrain)
        with open("wordList.txt", "wb") as fp: 
            pickle.dump(wordList, fp)
        
    numTrainingExamples = len(xTrain)
    vocabSize = len(wordList)

    sess = tf.Session()
    embeddingMatrix = tf.Variable(tf.random_uniform([vocabSize, wordVecDimensions], -1.0, 1.0))
    nceWeights = tf.Variable(tf.truncated_normal([vocabSize, wordVecDimensions], stddev=1.0 / math.sqrt(wordVecDimensions)))
    nceBiases = tf.Variable(tf.zeros([vocabSize]))

    inputs = tf.placeholder(tf.int32, shape=[batchSize])
    outputs = tf.placeholder(tf.int32, shape=[batchSize, 1])

    embed = tf.nn.embedding_lookup(embeddingMatrix, inputs)

    loss = tf.reduce_mean(
      tf.nn.nce_loss(weights=nceWeights,
                     biases=nceBiases,
                     labels=outputs,
                     inputs=embed,
                     num_sampled=numNegativeSample,
                     num_classes=vocabSize))

    optimizer = tf.train.GradientDescentOptimizer(learning_rate=1.0).minimize(loss)

    sess.run(tf.global_variables_initializer())
    for i in range(numIterations):
        trainInputs, trainLabels = getTrainingBatch()
        _, curLoss = sess.run([optimizer, loss], feed_dict={inputs: trainInputs, outputs: trainLabels})
        if (i % 10000 == 0):
            print ('Current loss is:', curLoss)
    print('Saving the word embedding matrix')
    embedMatrix = embeddingMatrix.eval(session=sess)
    np.save('embeddingMatrix.npy', embedMatrix)