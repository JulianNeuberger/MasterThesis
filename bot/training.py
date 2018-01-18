import logging
from datetime import datetime

import numpy
from keras.callbacks import TensorBoard
from keras.engine import Model

from bot.config import NUM_INTENTS, INTENTS, ACTIONS, BATCH_SIZE, NUM_EPOCHS, DISCOUNT, STATE_SHAPE
from bot.model import get_imagination_model, get_action_model
from data.processing import load_dumped

logger = logging.getLogger('bot')


def train_new_action_model():
    model = get_action_model()
    model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])
    model.summary()

    tensor_board_callback = TensorBoard(log_dir='./logs/{:%d-%m-%Y %H-%M}/'.format(datetime.now()),
                                        batch_size=BATCH_SIZE)
    train_contexts, test_contexts = load_dumped()

    train_xs = extract_state_contexts_from_transition_contexts(train_contexts)
    train_ys = numpy.array([context[0].action for context in train_contexts])
    test_xs = extract_state_contexts_from_transition_contexts(test_contexts)
    test_ys = numpy.array([context[0].action for context in test_contexts])
    model.fit(train_xs, train_ys, batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,
              validation_data=(test_xs, test_ys),
              callbacks=[tensor_board_callback])

    sample_context = test_xs[0]
    intent = sample_context[0][0:NUM_INTENTS]
    prediction = model.predict(numpy.array([sample_context]))[0]
    predicted_action = numpy.argmax(prediction)
    logger.info('Predicting action {} for intent {} based on {}'.format(
        ACTIONS[predicted_action],
        INTENTS[numpy.argmax(intent)],
        prettify_action_qualities(prediction)
    ))


def extract_state_contexts_from_transition_contexts(transition_contexts):
    state_contexts = []
    for context in transition_contexts:
        state_context = []
        for transition in context:
            if transition is not None:
                state_context.append(transition.state)
            else:
                state_context.append(numpy.zeros(STATE_SHAPE))
        state_contexts.append(state_context)
    return numpy.array(state_contexts)


def train_new_imagination_model():
    model = get_imagination_model()
    model.compile(optimizer='sgd', loss='binary_crossentropy')
    model.summary()

    tensor_board_callback = TensorBoard(log_dir='./logs/{:%d-%m-%Y %H-%M}/'.format(datetime.now()),
                                        batch_size=BATCH_SIZE)
    tensor_board_callback.set_model(model)

    training_transitions, test_transitions = load_dumped()
    for epoch in range(1, NUM_EPOCHS + 1):
        logger.info('Training epoch {}/{} starting'.format(epoch, NUM_EPOCHS))
        loss = train_on_transition_set(training_transitions, model)
        logger.info('Loss of epoch: {}'.format(loss))
        val_loss = test_on_transition_set(test_transitions, model)
        logger.info('Validation loss of epoch: {}'.format(val_loss))
        logs = {'loss': loss, 'val_loss': val_loss}
        tensor_board_callback.on_epoch_end(epoch, logs)

    # model.fit(train_xs, train_ys,
    #           batch_size=32, epochs=150,
    #           validation_data=(test_xs, test_ys),
    #           callbacks=[tensor_board])

    sample_state = test_transitions[1].state
    predictions = model.predict(numpy.array([sample_state]))
    intent = sample_state[0:NUM_INTENTS]
    intent_name = INTENTS[numpy.argmax(intent)]
    logger.info('Predicting action for intent "{}"'.format(
        intent_name
    ))
    logger.info('Predicting desired action is "{}"'.format(
        ACTIONS[numpy.argmax(predictions[0])]
    ))
    logger.info('Prediction based on quality vector [{}]"'.format(
        prettify_action_qualities(predictions[0])
    ))
    return model


def test_on_transition_set(transitions, model: Model):
    xs = numpy.array([transition.state for transition in transitions])
    ys = numpy.array([transition.get_quality(model, DISCOUNT) for transition in transitions])
    loss = model.evaluate(xs, ys, batch_size=BATCH_SIZE, verbose=0)
    return loss


def train_on_transition_set(transitions, model: Model):
    xs = []
    ys = []
    loss = 0
    i = 0
    for transition in transitions:
        xs.append(transition.state)
        ys.append(transition.get_quality(model, DISCOUNT))
        if len(xs) > BATCH_SIZE or len(transitions) - 1 == i:
            xs = numpy.array(xs)
            ys = numpy.array(ys)
            loss += model.train_on_batch(xs, ys)
            xs = []
            ys = []
        i += 1
    return loss / BATCH_SIZE


def prettify_action_qualities(vector):
    vector = zip(ACTIONS, vector)
    vector = sorted(vector, key=lambda x: x[1], reverse=True)
    return ', '.join('{} (Q={:.3})'.format(*entry) for entry in vector)
