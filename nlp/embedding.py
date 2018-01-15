import re

from gensim.models import KeyedVectors

from nlp.config import *


class EmbeddingProcessor:
    def __init__(self):
        super().__init__()
        self.language_model = KeyedVectors.load_word2vec_format(LANGUAGE_MODEL_PATH, binary=True)

    def process_single_sentence(self, sentence):
        sentence = self._split(sentence)
        sentence = [self._embed_word(word) for word in sentence]
        sentence = self._pad_with_zero(sentence)
        return sentence

    def _embed_word(self, word):
        if word not in self.language_model.vocab:
            return [0] * 300
        else:
            return self.language_model[word]

    @staticmethod
    def _pad_with_zero(sample):
        if len(sample) < SENTENCE_TOKEN_COUNT - 1:
            sample = [[0] * EMBEDDING_VECTOR_DIM] + sample + [[0] * EMBEDDING_VECTOR_DIM] * (
                SENTENCE_TOKEN_COUNT - len(sample) - 1)
        return sample

    @staticmethod
    def _split(sentence):
        raw_tokens = re.split('([^a-zA-Z0-9_äüöÄÜÖß]+)', sentence)
        return [raw_token for raw_token in raw_tokens if raw_token is not '' and raw_token != ' ']
