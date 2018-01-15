from bot.model import get_total_model
from data.processing import load_dumped


def train_new_model():
    model = get_total_model()
    model.compile(optimizer='sgd', loss='binary_crossentropy')
    model.summary()
    (train_xs, train_ys), (test_xs, test_ys) = load_dumped()
    model.fit(train_xs, train_ys, batch_size=32, epochs=1000, validation_data=(test_xs, test_ys))
    return model
