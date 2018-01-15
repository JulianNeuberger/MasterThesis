from keras.layers import Input, Dense

from nlp.config import *


def get_sentiment_model():
    sentence = Input(shape=(SENTENCE_TOKEN_COUNT, EMBEDDING_VECTOR_DIM, 1))
