from keras.engine import Layer


class StackLayer(Layer):
    def __init__(self, stack_size: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.stack_size = 1

    def build(self, input_shape):
        super().build(input_shape)

    def call(self, inputs, **kwargs):
        assert len(inputs) == 2, "First input needs to be the stack, second the one to stack on top"
        stack, to_add = inputs[0], inputs[1]

    def compute_output_shape(self, input_shape):
        return super().compute_output_shape(input_shape)
