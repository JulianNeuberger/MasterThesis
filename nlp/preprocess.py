import pickle

import numpy

from nlp.config import *
from nlp.embedding import EmbeddingProcessor


def pre_process_data():
    clean_data = get_clean_data()
    clean_data = shuffle_preprocessed_data(clean_data)
    train_data, test_data = split_preprocessed_data(clean_data, SENTIMENT_TEST_SPLIT)
    return train_data, test_data


def split_preprocessed_data(preprocessed_data, test_ratio):
    xs, ys = preprocessed_data
    split_index = int(len(xs) * (1 - test_ratio))
    return (xs[:split_index], ys[:split_index]), (xs[split_index:], ys[split_index:])


def shuffle_preprocessed_data(preprocessed_data):
    xs, ys = preprocessed_data
    assert len(xs) == len(ys)
    permutation = numpy.random.permutation(len(xs))
    xs = xs[permutation]
    ys = ys[permutation]
    return xs, ys


def get_clean_data():
    embedding_processor = EmbeddingProcessor()
    xs = []
    ys = []
    with open(SENTIMENT_RAW_DATA_FILE, 'r', encoding='utf-8') as raw_file:
        for raw_line in raw_file:
            sentence, sentiment = _get_sample_from_raw_values(_get_raw_values_from_line(raw_line), embedding_processor)
            xs.append(sentence)
            ys.append(sentiment)
    return numpy.array(xs), numpy.array(ys)


def _get_raw_values_from_line(line):
    return [line.split('\t')[i] for i in [1, 4]]


def _get_sample_from_raw_values(values, processor: EmbeddingProcessor):
    sentiment = _name_to_sentiment(values[0])
    sentence = processor.process_single_sentence(values[1])
    return sentence, sentiment


def _name_to_sentiment(sentiment_name: str):
    return 0 if sentiment_name == 'neutral' else 1 if sentiment_name == 'positive' else -1


if __name__ == '__main__':
    print('Pre processing data...')
    data = pre_process_data()
    print('Done!')
    print('Dumping pre processed data...')
    with open(PREPROCESSED_SENTIMENT_DATA_FILE, 'wb') as dump_file:
        pickle.dump(data, dump_file)
    print('Done! Quitting.')
