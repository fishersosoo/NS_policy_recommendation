import collections
import copy
import json
import math
import os
import re

import numpy as np
import six
import tensorflow as tf
from tensorflow.core.framework import types_pb2
from tensorflow.python import ops
from tensorflow.python.ops import math_ops, array_ops
from tensorflow.python.ops.losses.losses_impl import Reduction, _num_present, _num_elements, _safe_mean
from tensorflow.python.saved_model.signature_def_utils_impl import build_signature_def
from tensorflow.python.util.deprecation import deprecated_argument_lookup
from tensorflow.python.ops.losses import util
from tensorflow.python.ops import weights_broadcast_ops


def compute_weighted_loss(
        losses, weights=1.0, scope=None, loss_collection=ops.GraphKeys.LOSSES,
        reduction=Reduction.SUM_BY_NONZERO_WEIGHTS):
    """Computes the weighted loss.

    Args:
      losses: `Tensor` of shape `[batch_size, d1, ... dN]`.
      weights: Optional `Tensor` whose rank is either 0, or the same rank as
        `losses`, and must be broadcastable to `losses` (i.e., all dimensions must
        be either `1`, or the same as the corresponding `losses` dimension).
      scope: the scope for the operations performed in computing the loss.
      loss_collection: the loss will be added to these collections.
      reduction: Type of reduction to apply to loss.

    Returns:
      Weighted loss `Tensor` of the same type as `losses`. If `reduction` is
      `NONE`, this has the same shape as `losses`; otherwise, it is scalar.

    Raises:
      ValueError: If `weights` is `None` or the shape is not compatible with
        `losses`, or if the number of dimensions (rank) of either `losses` or
        `weights` is missing.

    Note:
      When calculating the gradient of a weighted loss contributions from
      both `losses` and `weights` are considered. If your `weights` depend
      on some model parameters but you do not want this to affect the loss
      gradient, you need to apply `tf.stop_gradient` to `weights` before
      passing them to `compute_weighted_loss`.

    @compatibility(eager)
    The `loss_collection` argument is ignored when executing eagerly. Consider
    holding on to the return value or collecting losses via a `tf.keras.Model`.
    @end_compatibility
    """
    Reduction.validate(reduction)
    with ops.name_scope(scope, "weighted_loss", (losses, weights)):
        # Save the `reduction` argument for loss normalization when distributing
        # to multiple towers.
        # TODO(josh11b): Associate it with the returned op for more precision.
        ops.get_default_graph()._last_loss_reduction = reduction  # pylint: disable=protected-access

        with ops.control_dependencies((
                weights_broadcast_ops.assert_broadcastable(weights, losses),)):
            losses = ops.convert_to_tensor(losses)
            input_dtype = losses.dtype
            losses = math_ops.to_float(losses)
            weights = math_ops.to_float(weights)
            weighted_losses = math_ops.multiply(losses, weights)
            if reduction == Reduction.NONE:
                loss = weighted_losses
            else:
                loss = math_ops.reduce_sum(weighted_losses)
                if reduction == Reduction.MEAN:
                    loss = _safe_mean(
                        loss,
                        math_ops.reduce_sum(array_ops.ones_like(losses) * weights))
                elif (reduction == Reduction.SUM_BY_NONZERO_WEIGHTS or
                      reduction == Reduction.SUM_OVER_NONZERO_WEIGHTS):
                    loss = _safe_mean(loss, _num_present(losses, weights))
                elif reduction == Reduction.SUM_OVER_BATCH_SIZE:
                    loss = tf.div_no_nan(loss, _num_elements(losses))

            # Convert the result back to the input type.
            loss = math_ops.cast(loss, input_dtype)
            util.add_loss(loss, loss_collection)
            return loss


def cosine_distance(
        labels, predictions, axis=None, weights=1.0, scope=None,
        loss_collection=ops.GraphKeys.LOSSES,
        reduction=Reduction.SUM_BY_NONZERO_WEIGHTS,
        dim=None):
    """Adds a cosine-distance loss to the training procedure.

    Note that the function assumes that `predictions` and `labels` are already
    unit-normalized.

    Args:
      labels: `Tensor` whose shape matches 'predictions'
      predictions: An arbitrary matrix.
      axis: The dimension along which the cosine distance is computed.
      weights: Optional `Tensor` whose rank is either 0, or the same rank as
        `labels`, and must be broadcastable to `labels` (i.e., all dimensions must
        be either `1`, or the same as the corresponding `losses` dimension).
      scope: The scope for the operations performed in computing the loss.
      loss_collection: collection to which this loss will be added.
      reduction: Type of reduction to apply to loss.
      dim: The old (deprecated) name for `axis`.

    Returns:
      Weighted loss float `Tensor`. If `reduction` is `NONE`, this has the same
      shape as `labels`; otherwise, it is scalar.

    Raises:
      ValueError: If `predictions` shape doesn't match `labels` shape, or
        `axis`, `labels`, `predictions` or `weights` is `None`.

    @compatibility(eager)
    The `loss_collection` argument is ignored when executing eagerly. Consider
    holding on to the return value or collecting losses via a `tf.keras.Model`.
    @end_compatibility
    """
    axis = deprecated_argument_lookup("axis", axis, "dim", dim)
    if axis is None:
        raise ValueError("You must specify 'axis'.")
    if labels is None:
        raise ValueError("labels must not be None.")
    if predictions is None:
        raise ValueError("predictions must not be None.")
    with ops.name_scope(scope, "cosine_distance_loss",
                        (predictions, labels, weights)) as scope:
        predictions = math_ops.to_float(predictions)
        labels = math_ops.to_float(labels)
        predictions.get_shape().assert_is_compatible_with(labels.get_shape())

        radial_diffs = math_ops.multiply(predictions, labels)
        losses = 1 - math_ops.reduce_sum(radial_diffs, axis=(axis,), keepdims=True)
        return compute_weighted_loss(
            losses, weights, scope, loss_collection, reduction=reduction)


def create_optimizer(loss, init_lr, num_train_steps, num_warmup_steps, use_tpu):
    """Creates an optimizer training op."""
    global_step = tf.train.get_or_create_global_step()

    learning_rate = tf.constant(value=init_lr, shape=[], dtype=tf.float32)

    # Implements linear decay of the learning rate.
    # learning_rate = tf.train.polynomial_decay(
    #     learning_rate,
    #     global_step,
    #     num_train_steps,
    #     end_learning_rate=0.0,
    #     power=1.0,
    #     cycle=False)

    # Implements linear warmup. I.e., if global_step < num_warmup_steps, the
    # learning rate will be `global_step/num_warmup_steps * init_lr`.
    if num_warmup_steps:
        global_steps_int = tf.cast(global_step, tf.int32)
        warmup_steps_int = tf.constant(num_warmup_steps, dtype=tf.int32)

        global_steps_float = tf.cast(global_steps_int, tf.float32)
        warmup_steps_float = tf.cast(warmup_steps_int, tf.float32)

        warmup_percent_done = global_steps_float / warmup_steps_float
        warmup_learning_rate = init_lr * warmup_percent_done

        is_warmup = tf.cast(global_steps_int < warmup_steps_int, tf.float32)
        learning_rate = (
                (1.0 - is_warmup) * learning_rate + is_warmup * warmup_learning_rate)

    # It is recommended that you use this optimizer for fine tuning, since this
    # is how the model was trained (note that the Adam m/v variables are NOT
    # loaded from init_checkpoint.)
    optimizer = AdamWeightDecayOptimizer(
        learning_rate=learning_rate,
        weight_decay_rate=0.01,
        beta_1=0.9,
        beta_2=0.999,
        epsilon=1e-6,
        exclude_from_weight_decay=["LayerNorm", "layer_norm", "bias"])

    if use_tpu:
        optimizer = tf.contrib.tpu.CrossShardOptimizer(optimizer)

    tvars = tf.trainable_variables()
    grads = tf.gradients(loss, tvars)

    # This is how the model was pre-trained.
    (grads, _) = tf.clip_by_global_norm(grads, clip_norm=1.0)

    train_op = optimizer.apply_gradients(
        zip(grads, tvars), global_step=global_step)

    # Normally the global step update is done inside of `apply_gradients`.
    # However, `AdamWeightDecayOptimizer` doesn't do this. But if you use
    # a different optimizer, you should probably take this line out.
    new_global_step = global_step + 1
    train_op = tf.group(train_op, [global_step.assign(new_global_step)])
    return train_op


class AdamWeightDecayOptimizer(tf.train.Optimizer):
    """A basic Adam optimizer that includes "correct" L2 weight decay."""

    def __init__(self,
                 learning_rate,
                 weight_decay_rate=0.0,
                 beta_1=0.9,
                 beta_2=0.999,
                 epsilon=1e-6,
                 exclude_from_weight_decay=None,
                 name="AdamWeightDecayOptimizer"):
        """Constructs a AdamWeightDecayOptimizer."""
        super(AdamWeightDecayOptimizer, self).__init__(False, name)

        self.learning_rate = learning_rate
        self.weight_decay_rate = weight_decay_rate
        self.beta_1 = beta_1
        self.beta_2 = beta_2
        self.epsilon = epsilon
        self.exclude_from_weight_decay = exclude_from_weight_decay

    def apply_gradients(self, grads_and_vars, global_step=None, name=None):
        """See base class."""
        assignments = []
        for (grad, param) in grads_and_vars:
            if grad is None or param is None:
                continue

            param_name = self._get_variable_name(param.name)

            m = tf.get_variable(
                name=param_name + "/adam_m",
                shape=param.shape.as_list(),
                dtype=tf.float32,
                trainable=False,
                initializer=tf.zeros_initializer())
            v = tf.get_variable(
                name=param_name + "/adam_v",
                shape=param.shape.as_list(),
                dtype=tf.float32,
                trainable=False,
                initializer=tf.zeros_initializer())

            # Standard Adam update.
            next_m = (
                    tf.multiply(self.beta_1, m) + tf.multiply(1.0 - self.beta_1, grad))
            next_v = (
                    tf.multiply(self.beta_2, v) + tf.multiply(1.0 - self.beta_2,
                                                              tf.square(grad)))

            update = next_m / (tf.sqrt(next_v) + self.epsilon)

            # Just adding the square of the weights to the loss function is *not*
            # the correct way of using L2 regularization/weight decay with Adam,
            # since that will interact with the m and v parameters in strange ways.
            #
            # Instead we want ot decay the weights in a manner that doesn't interact
            # with the m/v parameters. This is equivalent to adding the square
            # of the weights to the loss with plain (non-momentum) SGD.
            if self._do_use_weight_decay(param_name):
                update += self.weight_decay_rate * param

            update_with_lr = self.learning_rate * update

            next_param = param - update_with_lr

            assignments.extend(
                [param.assign(next_param),
                 m.assign(next_m),
                 v.assign(next_v)])
        return tf.group(*assignments, name=name)

    def _do_use_weight_decay(self, param_name):
        """Whether to use L2 weight decay for `param_name`."""
        if not self.weight_decay_rate:
            return False
        if self.exclude_from_weight_decay:
            for r in self.exclude_from_weight_decay:
                if re.search(r, param_name) is not None:
                    return False
        return True

    def _get_variable_name(self, param_name):
        """Get the variable name from the tensor name."""
        m = re.match("^(.*):\\d+$", param_name)
        if m is not None:
            param_name = m.group(1)
        return param_name


class ValueConfig(object):
    """Configuration for `BertModel`."""

    def __init__(self,
                 vocab_size,
                 hidden_size=768,
                 num_hidden_layers=12,
                 num_attention_heads=12,
                 intermediate_size=3072,
                 hidden_act="gelu",
                 hidden_dropout_prob=0.1,
                 attention_probs_dropout_prob=0.1,
                 max_position_embeddings=512,
                 type_vocab_size=16,
                 initializer_range=0.02):
        """Constructs BertConfig.

        Args:
          vocab_size: Vocabulary size of `inputs_ids` in `BertModel`.
          hidden_size: Size of the encoder layers and the pooler layer.
          num_hidden_layers: Number of hidden layers in the Transformer encoder.
          num_attention_heads: Number of attention heads for each attention layer in
            the Transformer encoder.
          intermediate_size: The size of the "intermediate" (i.e., feed-forward)
            layer in the Transformer encoder.
          hidden_act: The non-linear activation function (function or string) in the
            encoder and pooler.
          hidden_dropout_prob: The dropout probability for all fully connected
            layers in the embeddings, encoder, and pooler.
          attention_probs_dropout_prob: The dropout ratio for the attention
            probabilities.
          max_position_embeddings: The maximum sequence length that this model might
            ever be used with. Typically set this to something large just in case
            (e.g., 512 or 1024 or 2048).
          type_vocab_size: The vocabulary size of the `token_type_ids` passed into
            `BertModel`.
          initializer_range: The stdev of the truncated_normal_initializer for
            initializing all weight matrices.
        """
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.intermediate_size = intermediate_size
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.type_vocab_size = type_vocab_size
        self.initializer_range = initializer_range

    @classmethod
    def from_dict(cls, json_object):
        """Constructs a `BertConfig` from a Python dictionary of parameters."""
        config = ValueConfig(vocab_size=None)
        for (key, value) in six.iteritems(json_object):
            config.__dict__[key] = value
        return config

    @classmethod
    def from_json_file(cls, json_file):
        """Constructs a `BertConfig` from a json file of parameters."""
        with tf.gfile.GFile(json_file, "r") as reader:
            text = reader.read()
        return cls.from_dict(json.loads(text))

    def to_dict(self):
        """Serializes this instance to a Python dictionary."""
        output = copy.deepcopy(self.__dict__)
        return output

    def to_json_string(self):
        """Serializes this instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


def assert_rank(tensor, expected_rank, name=None):
    """Raises an exception if the tensor rank is not of the expected rank.

    Args:
      tensor: A tf.Tensor to check the rank of.
      expected_rank: Python integer or list of integers, expected rank.
      name: Optional name of the tensor for the error message.

    Raises:
      ValueError: If the expected shape doesn't match the actual shape.
    """
    if name is None:
        name = tensor.name

    expected_rank_dict = {}
    if isinstance(expected_rank, six.integer_types):
        expected_rank_dict[expected_rank] = True
    else:
        for x in expected_rank:
            expected_rank_dict[x] = True

    actual_rank = tensor.shape.ndims
    if actual_rank not in expected_rank_dict:
        scope_name = tf.get_variable_scope().name
        raise ValueError(
            "For the tensor `%s` in scope `%s`, the actual rank "
            "`%d` (shape = %s) is not equal to the expected rank `%s`" %
            (name, scope_name, actual_rank, str(tensor.shape), str(expected_rank)))


def get_shape_list(tensor, expected_rank=None, name=None):
    """Returns a list of the shape of tensor, preferring static dimensions.

    Args:
      tensor: A tf.Tensor object to find the shape of.
      expected_rank: (optional) int. The expected rank of `tensor`. If this is
        specified and the `tensor` has a different rank, and exception will be
        thrown.
      name: Optional name of the tensor for the error message.

    Returns:
      A list of dimensions of the shape of tensor. All static dimensions will
      be returned as python integers, and dynamic dimensions will be returned
      as tf.Tensor scalars.
    """
    if name is None:
        name = tensor.name

    if expected_rank is not None:
        assert_rank(tensor, expected_rank, name)

    shape = tensor.shape.as_list()

    non_static_indexes = []
    for (index, dim) in enumerate(shape):
        if dim is None:
            non_static_indexes.append(index)

    if not non_static_indexes:
        return shape

    dyn_shape = tf.shape(tensor)
    for index in non_static_indexes:
        shape[index] = dyn_shape[index]
    return shape


def create_initializer(initializer_range=0.02):
    """Creates a `truncated_normal_initializer` with the given range."""
    return tf.truncated_normal_initializer(stddev=initializer_range)


def get_activation(activation_string):
    """Maps a string to a Python function, e.g., "relu" => `tf.nn.relu`.

    Args:
      activation_string: String name of the activation function.

    Returns:
      A Python function corresponding to the activation function. If
      `activation_string` is None, empty, or "linear", this will return None.
      If `activation_string` is not a string, it will return `activation_string`.

    Raises:
      ValueError: The `activation_string` does not correspond to a known
        activation.
    """

    # We assume that anything that"s not a string is already an activation
    # function, so we just return it.
    if not isinstance(activation_string, six.string_types):
        return activation_string

    if not activation_string:
        return None

    act = activation_string.lower()
    if act == "linear":
        return None
    elif act == "relu":
        return tf.nn.relu
    elif act == "gelu":
        return gelu
    elif act == "tanh":
        return tf.tanh
    else:
        raise ValueError("Unsupported activation: %s" % act)


def embedding_lookup(input_ids,
                     vocab_size,
                     embedding_size=128,
                     initializer_range=0.02,
                     word_embedding_name="word_embeddings",
                     use_one_hot_embeddings=False):
    """Looks up words embeddings for id tensor.

    Args:
      input_ids: int32 Tensor of shape [batch_size, seq_length] containing word
        ids.
      vocab_size: int. Size of the embedding vocabulary.
      embedding_size: int. Width of the word embeddings.
      initializer_range: float. Embedding initialization range.
      word_embedding_name: string. Name of the embedding table.
      use_one_hot_embeddings: bool. If True, use one-hot method for word
        embeddings. If False, use `tf.gather()`.

    Returns:
      float Tensor of shape [batch_size, seq_length, embedding_size].
    """
    # This function assumes that the input is of shape [batch_size, seq_length,
    # num_inputs].
    #
    # If the input is a 2D tensor of shape [batch_size, seq_length], we
    # reshape to [batch_size, seq_length, 1].
    if input_ids.shape.ndims == 2:
        input_ids = tf.expand_dims(input_ids, axis=[-1])

    embedding_table = tf.get_variable(
        name=word_embedding_name,
        shape=[vocab_size, embedding_size],
        initializer=create_initializer(initializer_range))

    flat_input_ids = tf.reshape(input_ids, [-1])
    if use_one_hot_embeddings:
        one_hot_input_ids = tf.one_hot(flat_input_ids, depth=vocab_size)
        output = tf.matmul(one_hot_input_ids, embedding_table)
    else:
        output = tf.gather(embedding_table, flat_input_ids)

    input_shape = get_shape_list(input_ids)

    output = tf.reshape(output,
                        input_shape[0:-1] + [input_shape[-1] * embedding_size])
    return (output, embedding_table)


def layer_norm(input_tensor, name=None):
    """Run layer normalization on the last dimension of the tensor."""
    return tf.contrib.layers.layer_norm(
        inputs=input_tensor, begin_norm_axis=-1, begin_params_axis=-1, scope=name)


def dropout(input_tensor, dropout_prob):
    """Perform dropout.

    Args:
      input_tensor: float Tensor.
      dropout_prob: Python float. The probability of dropping out a value (NOT of
        *keeping* a dimension as in `tf.nn.dropout`).

    Returns:
      A version of `input_tensor` with dropout applied.
    """
    if dropout_prob is None or dropout_prob == 0.0:
        return input_tensor

    output = tf.nn.dropout(input_tensor, 1.0 - dropout_prob)
    return output


def layer_norm_and_dropout(input_tensor, dropout_prob, name=None):
    """Runs layer normalization followed by dropout."""
    output_tensor = layer_norm(input_tensor, name)
    output_tensor = dropout(output_tensor, dropout_prob)
    return output_tensor


def embedding_postprocessor(input_tensor,
                            use_token_type=False,
                            token_type_ids=None,
                            token_type_vocab_size=16,
                            token_type_embedding_name="token_type_embeddings",
                            use_position_embeddings=True,
                            position_embedding_name="position_embeddings",
                            initializer_range=0.02,
                            max_position_embeddings=512,
                            dropout_prob=0.1):
    """Performs various post-processing on a word embedding tensor.

    Args:
      input_tensor: float Tensor of shape [batch_size, seq_length,
        embedding_size].
      use_token_type: bool. Whether to add embeddings for `token_type_ids`.
      token_type_ids: (optional) int32 Tensor of shape [batch_size, seq_length].
        Must be specified if `use_token_type` is True.
      token_type_vocab_size: int. The vocabulary size of `token_type_ids`.
      token_type_embedding_name: string. The name of the embedding table variable
        for token type ids.
      use_position_embeddings: bool. Whether to add position embeddings for the
        position of each token in the sequence.
      position_embedding_name: string. The name of the embedding table variable
        for positional embeddings.
      initializer_range: float. Range of the weight initialization.
      max_position_embeddings: int. Maximum sequence length that might ever be
        used with this model. This can be longer than the sequence length of
        input_tensor, but cannot be shorter.
      dropout_prob: float. Dropout probability applied to the final output tensor.

    Returns:
      float tensor with same shape as `input_tensor`.

    Raises:
      ValueError: One of the tensor shapes or input values is invalid.
    """
    input_shape = get_shape_list(input_tensor, expected_rank=3)
    batch_size = input_shape[0]
    seq_length = input_shape[1]
    width = input_shape[2]

    output = input_tensor

    if use_token_type:
        if token_type_ids is None:
            raise ValueError("`token_type_ids` must be specified if"
                             "`use_token_type` is True.")
        token_type_table = tf.get_variable(
            name=token_type_embedding_name,
            shape=[token_type_vocab_size, width],
            initializer=create_initializer(initializer_range))
        # This vocab will be small so we always do one-hot here, since it is always
        # faster for a small vocabulary.
        flat_token_type_ids = tf.reshape(token_type_ids, [-1])
        one_hot_ids = tf.one_hot(flat_token_type_ids, depth=token_type_vocab_size)
        token_type_embeddings = tf.matmul(one_hot_ids, token_type_table)
        token_type_embeddings = tf.reshape(token_type_embeddings,
                                           [batch_size, seq_length, width])
        output += token_type_embeddings

    if use_position_embeddings:
        assert_op = tf.assert_less_equal(seq_length, max_position_embeddings)
        with tf.control_dependencies([assert_op]):
            full_position_embeddings = tf.get_variable(
                name=position_embedding_name,
                shape=[max_position_embeddings, width],
                initializer=create_initializer(initializer_range))
            # Since the position embedding table is a learned variable, we create it
            # using a (long) sequence length `max_position_embeddings`. The actual
            # sequence length might be shorter than this, for faster training of
            # tasks that do not have long sequences.
            #
            # So `full_position_embeddings` is effectively an embedding table
            # for position [0, 1, 2, ..., max_position_embeddings-1], and the current
            # sequence has positions [0, 1, 2, ... seq_length-1], so we can just
            # perform a slice.
            position_embeddings = tf.slice(full_position_embeddings, [0, 0],
                                           [seq_length, -1])
            num_dims = len(output.shape.as_list())

            # Only the last two dimensions are relevant (`seq_length` and `width`), so
            # we broadcast among the first dimensions, which is typically just
            # the batch size.
            position_broadcast_shape = []
            for _ in range(num_dims - 2):
                position_broadcast_shape.append(1)
            position_broadcast_shape.extend([seq_length, width])
            position_embeddings = tf.reshape(position_embeddings,
                                             position_broadcast_shape)
            output += position_embeddings

    output = layer_norm_and_dropout(output, dropout_prob)
    return output


def create_attention_mask_from_input_mask(from_tensor, to_mask):
    """Create 3D attention mask from a 2D tensor mask.

    Args:
      from_tensor: 2D or 3D Tensor of shape [batch_size, from_seq_length, ...].
      to_mask: int32 Tensor of shape [batch_size, to_seq_length].

    Returns:
      float Tensor of shape [batch_size, from_seq_length, to_seq_length].
    """
    from_shape = get_shape_list(from_tensor, expected_rank=[2, 3])
    batch_size = from_shape[0]
    from_seq_length = from_shape[1]

    to_shape = get_shape_list(to_mask, expected_rank=2)
    to_seq_length = to_shape[1]

    to_mask = tf.cast(
        tf.reshape(to_mask, [batch_size, 1, to_seq_length]), tf.float32)

    # We don't assume that `from_tensor` is a mask (although it could be). We
    # don't actually care if we attend *from* padding tokens (only *to* padding)
    # tokens so we create a tensor of all ones.
    #
    # `broadcast_ones` = [batch_size, from_seq_length, 1]
    broadcast_ones = tf.ones(
        shape=[batch_size, from_seq_length, 1], dtype=tf.float32)

    # Here we broadcast along two dimensions to create the mask.
    mask = broadcast_ones * to_mask

    return mask


def reshape_to_matrix(input_tensor):
    """Reshapes a >= rank 2 tensor to a rank 2 tensor (i.e., a matrix)."""
    ndims = input_tensor.shape.ndims
    if ndims < 2:
        raise ValueError("Input tensor must have at least rank 2. Shape = %s" %
                         (input_tensor.shape))
    if ndims == 2:
        return input_tensor

    width = input_tensor.shape[-1]
    output_tensor = tf.reshape(input_tensor, [-1, width])
    return output_tensor


def attention_layer(from_tensor,
                    to_tensor,
                    attention_mask=None,
                    num_attention_heads=1,
                    size_per_head=512,
                    query_act=None,
                    key_act=None,
                    value_act=None,
                    attention_probs_dropout_prob=0.0,
                    initializer_range=0.02,
                    do_return_2d_tensor=False,
                    batch_size=None,
                    from_seq_length=None,
                    to_seq_length=None):
    """Performs multi-headed attention from `from_tensor` to `to_tensor`.

    This is an implementation of multi-headed attention based on "Attention
    is all you Need". If `from_tensor` and `to_tensor` are the same, then
    this is self-attention. Each timestep in `from_tensor` attends to the
    corresponding sequence in `to_tensor`, and returns a fixed-with vector.

    This function first projects `from_tensor` into a "query" tensor and
    `to_tensor` into "key" and "value" tensors. These are (effectively) a list
    of tensors of length `num_attention_heads`, where each tensor is of shape
    [batch_size, seq_length, size_per_head].

    Then, the query and key tensors are dot-producted and scaled. These are
    softmaxed to obtain attention probabilities. The value tensors are then
    interpolated by these probabilities, then concatenated back to a single
    tensor and returned.

    In practice, the multi-headed attention are done with transposes and
    reshapes rather than actual separate tensors.

    Args:
      from_tensor: float Tensor of shape [batch_size, from_seq_length,
        from_width].
      to_tensor: float Tensor of shape [batch_size, to_seq_length, to_width].
      attention_mask: (optional) int32 Tensor of shape [batch_size,
        from_seq_length, to_seq_length]. The values should be 1 or 0. The
        attention scores will effectively be set to -infinity for any positions in
        the mask that are 0, and will be unchanged for positions that are 1.
      num_attention_heads: int. Number of attention heads.
      size_per_head: int. Size of each attention head.
      query_act: (optional) Activation function for the query transform.
      key_act: (optional) Activation function for the key transform.
      value_act: (optional) Activation function for the value transform.
      attention_probs_dropout_prob: (optional) float. Dropout probability of the
        attention probabilities.
      initializer_range: float. Range of the weight initializer.
      do_return_2d_tensor: bool. If True, the output will be of shape [batch_size
        * from_seq_length, num_attention_heads * size_per_head]. If False, the
        output will be of shape [batch_size, from_seq_length, num_attention_heads
        * size_per_head].
      batch_size: (Optional) int. If the input is 2D, this might be the batch size
        of the 3D version of the `from_tensor` and `to_tensor`.
      from_seq_length: (Optional) If the input is 2D, this might be the seq length
        of the 3D version of the `from_tensor`.
      to_seq_length: (Optional) If the input is 2D, this might be the seq length
        of the 3D version of the `to_tensor`.

    Returns:
      float Tensor of shape [batch_size, from_seq_length,
        num_attention_heads * size_per_head]. (If `do_return_2d_tensor` is
        true, this will be of shape [batch_size * from_seq_length,
        num_attention_heads * size_per_head]).

    Raises:
      ValueError: Any of the arguments or tensor shapes are invalid.
    """

    def transpose_for_scores(input_tensor, batch_size, num_attention_heads,
                             seq_length, width):
        output_tensor = tf.reshape(
            input_tensor, [batch_size, seq_length, num_attention_heads, width])

        output_tensor = tf.transpose(output_tensor, [0, 2, 1, 3])
        return output_tensor

    from_shape = get_shape_list(from_tensor, expected_rank=[2, 3])
    to_shape = get_shape_list(to_tensor, expected_rank=[2, 3])

    if len(from_shape) != len(to_shape):
        raise ValueError(
            "The rank of `from_tensor` must match the rank of `to_tensor`.")

    if len(from_shape) == 3:
        batch_size = from_shape[0]
        from_seq_length = from_shape[1]
        to_seq_length = to_shape[1]
    elif len(from_shape) == 2:
        if batch_size is None or from_seq_length is None or to_seq_length is None:
            raise ValueError(
                "When passing in rank 2 tensors to attention_layer, the values "
                "for `batch_size`, `from_seq_length`, and `to_seq_length` "
                "must all be specified.")

    # Scalar dimensions referenced here:
    #   B = batch size (number of sequences)
    #   F = `from_tensor` sequence length
    #   T = `to_tensor` sequence length
    #   N = `num_attention_heads`
    #   H = `size_per_head`

    from_tensor_2d = reshape_to_matrix(from_tensor)
    to_tensor_2d = reshape_to_matrix(to_tensor)

    # `query_layer` = [B*F, N*H]
    query_layer = tf.layers.dense(
        from_tensor_2d,
        num_attention_heads * size_per_head,
        activation=query_act,
        name="query",
        kernel_initializer=create_initializer(initializer_range))

    # `key_layer` = [B*T, N*H]
    key_layer = tf.layers.dense(
        to_tensor_2d,
        num_attention_heads * size_per_head,
        activation=key_act,
        name="key",
        kernel_initializer=create_initializer(initializer_range))

    # `value_layer` = [B*T, N*H]
    value_layer = tf.layers.dense(
        to_tensor_2d,
        num_attention_heads * size_per_head,
        activation=value_act,
        name="value",
        kernel_initializer=create_initializer(initializer_range))

    # `query_layer` = [B, N, F, H]
    query_layer = transpose_for_scores(query_layer, batch_size,
                                       num_attention_heads, from_seq_length,
                                       size_per_head)

    # `key_layer` = [B, N, T, H]
    key_layer = transpose_for_scores(key_layer, batch_size, num_attention_heads,
                                     to_seq_length, size_per_head)

    # Take the dot product between "query" and "key" to get the raw
    # attention scores.
    # `attention_scores` = [B, N, F, T]
    attention_scores = tf.matmul(query_layer, key_layer, transpose_b=True)
    attention_scores = tf.multiply(attention_scores,
                                   1.0 / math.sqrt(float(size_per_head)))

    if attention_mask is not None:
        # `attention_mask` = [B, 1, F, T]
        attention_mask = tf.expand_dims(attention_mask, axis=[1])

        # Since attention_mask is 1.0 for positions we want to attend and 0.0 for
        # masked positions, this operation will create a tensor which is 0.0 for
        # positions we want to attend and -10000.0 for masked positions.
        adder = (1.0 - tf.cast(attention_mask, tf.float32)) * -10000.0

        # Since we are adding it to the raw scores before the softmax, this is
        # effectively the same as removing these entirely.
        attention_scores += adder

    # Normalize the attention scores to probabilities.
    # `attention_probs` = [B, N, F, T]
    attention_probs = tf.nn.softmax(attention_scores)

    # This is actually dropping out entire tokens to attend to, which might
    # seem a bit unusual, but is taken from the original Transformer paper.
    attention_probs = dropout(attention_probs, attention_probs_dropout_prob)

    # `value_layer` = [B, T, N, H]
    value_layer = tf.reshape(
        value_layer,
        [batch_size, to_seq_length, num_attention_heads, size_per_head])

    # `value_layer` = [B, N, T, H]
    value_layer = tf.transpose(value_layer, [0, 2, 1, 3])

    # `context_layer` = [B, N, F, H]
    context_layer = tf.matmul(attention_probs, value_layer)

    # `context_layer` = [B, F, N, H]
    context_layer = tf.transpose(context_layer, [0, 2, 1, 3])

    if do_return_2d_tensor:
        # `context_layer` = [B*F, N*H]
        context_layer = tf.reshape(
            context_layer,
            [batch_size * from_seq_length, num_attention_heads * size_per_head])
    else:
        # `context_layer` = [B, F, N*H]
        context_layer = tf.reshape(
            context_layer,
            [batch_size, from_seq_length, num_attention_heads * size_per_head])

    return context_layer


def gelu(x):
    """Gaussian Error Linear Unit.

    This is a smoother version of the RELU.
    Original paper: https://arxiv.org/abs/1606.08415
    Args:
      x: float Tensor to perform activation.

    Returns:
      `x` with the GELU activation applied.
    """
    cdf = 0.5 * (1.0 + tf.tanh(
        (np.sqrt(2 / np.pi) * (x + 0.044715 * tf.pow(x, 3)))))
    return x * cdf


def reshape_from_matrix(output_tensor, orig_shape_list):
    """Reshapes a rank 2 tensor back to its original rank >= 2 tensor."""
    if len(orig_shape_list) == 2:
        return output_tensor

    output_shape = get_shape_list(output_tensor)

    orig_dims = orig_shape_list[0:-1]
    width = output_shape[-1]

    return tf.reshape(output_tensor, orig_dims + [width])


def transformer_model(input_tensor,
                      attention_mask=None,
                      hidden_size=768,
                      num_hidden_layers=12,
                      num_attention_heads=12,
                      intermediate_size=3072,
                      intermediate_act_fn=gelu,
                      hidden_dropout_prob=0.1,
                      attention_probs_dropout_prob=0.1,
                      initializer_range=0.02,
                      do_return_all_layers=False):
    """Multi-headed, multi-layer Transformer from "Attention is All You Need".

    This is almost an exact implementation of the original Transformer encoder.

    See the original paper:
    https://arxiv.org/abs/1706.03762

    Also see:
    https://github.com/tensorflow/tensor2tensor/blob/master/tensor2tensor/models/transformer.py

    Args:
      input_tensor: float Tensor of shape [batch_size, seq_length, hidden_size].
      attention_mask: (optional) int32 Tensor of shape [batch_size, seq_length,
        seq_length], with 1 for positions that can be attended to and 0 in
        positions that should not be.
      hidden_size: int. Hidden size of the Transformer.
      num_hidden_layers: int. Number of layers (blocks) in the Transformer.
      num_attention_heads: int. Number of attention heads in the Transformer.
      intermediate_size: int. The size of the "intermediate" (a.k.a., feed
        forward) layer.
      intermediate_act_fn: function. The non-linear activation function to apply
        to the output of the intermediate/feed-forward layer.
      hidden_dropout_prob: float. Dropout probability for the hidden layers.
      attention_probs_dropout_prob: float. Dropout probability of the attention
        probabilities.
      initializer_range: float. Range of the initializer (stddev of truncated
        normal).
      do_return_all_layers: Whether to also return all layers or just the final
        layer.

    Returns:
      float Tensor of shape [batch_size, seq_length, hidden_size], the final
      hidden layer of the Transformer.

    Raises:
      ValueError: A Tensor shape or parameter is invalid.
    """
    if hidden_size % num_attention_heads != 0:
        raise ValueError(
            "The hidden size (%d) is not a multiple of the number of attention "
            "heads (%d)" % (hidden_size, num_attention_heads))

    attention_head_size = int(hidden_size / num_attention_heads)
    input_shape = get_shape_list(input_tensor, expected_rank=3)
    batch_size = input_shape[0]
    seq_length = input_shape[1]
    input_width = input_shape[2]

    # The Transformer performs sum residuals on all layers so the input needs
    # to be the same as the hidden size.
    if input_width != hidden_size:
        raise ValueError("The width of the input tensor (%d) != hidden size (%d)" %
                         (input_width, hidden_size))

    # We keep the representation as a 2D tensor to avoid re-shaping it back and
    # forth from a 3D tensor to a 2D tensor. Re-shapes are normally free on
    # the GPU/CPU but may not be free on the TPU, so we want to minimize them to
    # help the optimizer.
    prev_output = reshape_to_matrix(input_tensor)

    all_layer_outputs = []
    for layer_idx in range(num_hidden_layers):
        with tf.variable_scope("layer_%d" % layer_idx):
            layer_input = prev_output

            with tf.variable_scope("attention"):
                attention_heads = []
                with tf.variable_scope("self"):
                    attention_head = attention_layer(
                        from_tensor=layer_input,
                        to_tensor=layer_input,
                        attention_mask=attention_mask,
                        num_attention_heads=num_attention_heads,
                        size_per_head=attention_head_size,
                        attention_probs_dropout_prob=attention_probs_dropout_prob,
                        initializer_range=initializer_range,
                        do_return_2d_tensor=True,
                        batch_size=batch_size,
                        from_seq_length=seq_length,
                        to_seq_length=seq_length)
                    attention_heads.append(attention_head)

                attention_output = None
                if len(attention_heads) == 1:
                    attention_output = attention_heads[0]
                else:
                    # In the case where we have other sequences, we just concatenate
                    # them to the self-attention head before the projection.
                    attention_output = tf.concat(attention_heads, axis=-1)

                # Run a linear projection of `hidden_size` then add a residual
                # with `layer_input`.
                with tf.variable_scope("output"):
                    attention_output = tf.layers.dense(
                        attention_output,
                        hidden_size,
                        kernel_initializer=create_initializer(initializer_range))
                    attention_output = dropout(attention_output, hidden_dropout_prob)
                    attention_output = layer_norm(attention_output + layer_input)

            # The activation is only applied to the "intermediate" hidden layer.
            with tf.variable_scope("intermediate"):
                intermediate_output = tf.layers.dense(
                    attention_output,
                    intermediate_size,
                    activation=intermediate_act_fn,
                    kernel_initializer=create_initializer(initializer_range))

            # Down-project back to `hidden_size` then add the residual.
            with tf.variable_scope("output"):
                layer_output = tf.layers.dense(
                    intermediate_output,
                    hidden_size,
                    kernel_initializer=create_initializer(initializer_range))
                layer_output = dropout(layer_output, hidden_dropout_prob)
                layer_output = layer_norm(layer_output + attention_output)
                prev_output = layer_output
                all_layer_outputs.append(layer_output)

    if do_return_all_layers:
        final_outputs = []
        for layer_output in all_layer_outputs:
            final_output = reshape_from_matrix(layer_output, input_shape)
            final_outputs.append(final_output)
        return final_outputs
    else:
        final_output = reshape_from_matrix(prev_output, input_shape)
        return final_output


# def decode(helper, scope, reuse=None):
#     with tf.variable_scope(scope, reuse=reuse):
#         attention_mechanism = tf.contrib.seq2seq.BahdanauAttention(
#             num_units=num_units, memory=encoder_outputs,
#             memory_sequence_length=input_lengths)
#         cell = tf.contrib.rnn.GRUCell(num_units=num_units)
#         attn_cell = tf.contrib.seq2seq.AttentionWrapper(
#             cell, attention_mechanism, attention_layer_size=num_units / 2)
#         out_cell = tf.contrib.rnn.OutputProjectionWrapper(
#             attn_cell, vocab_size, reuse=reuse
#         )
#         decoder = tf.contrib.seq2seq.BasicDecoder(
#             cell=out_cell, helper=helper,
#             initial_state=out_cell.zero_state(
#                 dtype=tf.float32, batch_size=batch_size))
#             #initial_state=encoder_final_state)
#         outputs = tf.contrib.seq2seq.dynamic_decode(
#             decoder=decoder, output_time_major=False,
#             impute_finished=True, maximum_iterations=output_max_length
#         )
#         return outputs[0]

class Value2FieldModel:
    def __init__(self,
                 config,
                 is_training,
                 input_ids,
                 input_mask=None,
                 scope=None):
        config = copy.deepcopy(config)
        if not is_training:
            config.dropout_prob = .0
        input_shape = get_shape_list(input_ids, expected_rank=2)
        batch_size = input_shape[0]
        seq_length = input_shape[1]
        if input_mask is None:
            input_mask = tf.ones(shape=[batch_size, seq_length], dtype=tf.int32)

        with tf.variable_scope(scope, default_name="seq2seq"):
            with tf.variable_scope("embeddings"):
                (self.embedding_output, self.embedding_table) = embedding_lookup(
                    input_ids=input_ids,
                    vocab_size=config.vocab_size,
                    embedding_size=config.hidden_size,
                    initializer_range=config.initializer_range,
                    word_embedding_name="word_embeddings",
                    use_one_hot_embeddings=False)

                # Add positional embeddings and token type embeddings, then layer
                # normalize and perform dropout.
                self.embedding_output = embedding_postprocessor(
                    input_tensor=self.embedding_output,
                    use_token_type=False,
                    token_type_ids=None,
                    token_type_vocab_size=config.type_vocab_size,
                    token_type_embedding_name="token_type_embeddings",
                    use_position_embeddings=True,
                    position_embedding_name="position_embeddings",
                    initializer_range=config.initializer_range,
                    max_position_embeddings=config.max_position_embeddings,
                    dropout_prob=config.hidden_dropout_prob)
        with tf.variable_scope("encoder"):
            # This converts a 2D mask of shape [batch_size, seq_length] to a 3D
            # mask of shape [batch_size, seq_length, seq_length] which is used
            # for the attention scores.
            attention_mask = create_attention_mask_from_input_mask(
                input_ids, input_mask)
            # Run the stacked transformer.
            # `sequence_output` shape = [batch_size, seq_length, hidden_size].
            self.all_encoder_layers = transformer_model(
                input_tensor=self.embedding_output,
                attention_mask=attention_mask,
                hidden_size=config.hidden_size,
                num_hidden_layers=config.num_hidden_layers,
                num_attention_heads=config.num_attention_heads,
                intermediate_size=config.intermediate_size,
                intermediate_act_fn=get_activation(config.hidden_act),
                hidden_dropout_prob=config.hidden_dropout_prob,
                attention_probs_dropout_prob=config.attention_probs_dropout_prob,
                initializer_range=config.initializer_range,
                do_return_all_layers=True)
            self.sequence_output = self.all_encoder_layers[-1]
        with tf.variable_scope("pooler"):
            # We "pool" the model by simply taking the hidden state corresponding
            # to the first token. We assume that this has been pre-trained
            first_token_tensor = tf.squeeze(self.sequence_output[:, 0:1, :], axis=1)
            self.pooled_output = tf.layers.dense(
                first_token_tensor,
                config.hidden_size,
                activation=tf.tanh,
                kernel_initializer=create_initializer(config.initializer_range))

    def get_pooled_output(self):
        return self.pooled_output

    def get_sequence_output(self):
        """Gets final hidden layer of encoder.

        Returns:
          float Tensor of shape [batch_size, seq_length, hidden_size] corresponding
          to the final hidden of the transformer encoder.
        """
        return self.sequence_output

    def get_all_encoder_layers(self):
        return self.all_encoder_layers

    def get_embedding_output(self):
        """Gets output of the embedding lookup (i.e., input to the transformer).

        Returns:
          float Tensor of shape [batch_size, seq_length, hidden_size] corresponding
          to the output of the embedding layer, after summing the word
          embeddings with the positional embeddings and the token type embeddings,
          then performing layer normalization. This is the input to the transformer.
        """
        return self.embedding_output

    def get_embedding_table(self):
        return self.embedding_table


def create_model(config, is_training, input_ids, input_mask, output_ids, output_mask):
    model = Value2FieldModel(
        config=config,
        is_training=is_training,
        input_ids=input_ids,
        input_mask=input_mask)
    output_layer = model.pooled_output
    if is_training:
        output_layer = tf.nn.dropout(output_layer, keep_prob=0.9)
    with tf.variable_scope("output_embeddings"):
        (output_embedding, output_embedding_table) = embedding_lookup(
            input_ids=output_ids,
            vocab_size=config.vocab_size,
            embedding_size=config.hidden_size,
            initializer_range=config.initializer_range,
            word_embedding_name="output_embeddings",
            use_one_hot_embeddings=False)

        # Add positional embeddings and token type embeddings, then layer
        # normalize and perform dropout.
        if is_training:
            hidden_dropout_prob = config.hidden_dropout_prob
        else:
            hidden_dropout_prob = 0.
        output_embedding = embedding_postprocessor(
            input_tensor=output_embedding,
            use_token_type=False,
            token_type_ids=None,
            token_type_vocab_size=config.type_vocab_size,
            token_type_embedding_name="output_token_type_embeddings",
            use_position_embeddings=True,
            position_embedding_name="output_position_embeddings",
            initializer_range=config.initializer_range,
            max_position_embeddings=config.max_position_embeddings,
            dropout_prob=hidden_dropout_prob)
        # with tf.variable_scope("pooler", reuse=True):
        output_embedding = tf.squeeze(output_embedding[:, 0:1, :], axis=1)
    # output_logits = tf.layers.dense(
    #     output_layer,
    #     config.vocab_size,
    #     activation=tf.tanh,
    #     kernel_initializer=create_initializer(config.initializer_range))
    # predict_ids = tf.argmax(output_logits, axis=-1, output_type=tf.int32)
    with tf.variable_scope("loss"):
        output_embedding = tf.nn.l2_normalize(output_embedding, axis=1)
        predict_embedding = tf.nn.l2_normalize(output_layer, axis=1)
        loss = cosine_distance(output_embedding, predict_embedding,
                               axis=1,
                               reduction=Reduction.SUM_OVER_BATCH_SIZE)
        # loss = tf.contrib.seq2seq.sequence_loss(
        #     output_logits,
        #     output_ids,
        #     output_mask, name="loss")
    return (loss, output_embedding, model.all_encoder_layers[-2])


def get_assignment_map_from_checkpoint(tvars, init_checkpoint):
    """Compute the union of the current variables and checkpoint variables."""
    assignment_map = {}
    initialized_variable_names = {}
    name_to_variable = collections.OrderedDict()
    for var in tvars:
        name = var.name
        m = re.match("^(.*):\\d+$", name)
        if m is not None:
            name = m.group(1)
        name_to_variable[name] = var

    init_vars = tf.train.list_variables(init_checkpoint)

    assignment_map = collections.OrderedDict()
    for x in init_vars:
        (name, var) = (x[0], x[1])
        if name not in name_to_variable:
            continue
        assignment_map[name] = name
        initialized_variable_names[name] = 1
        initialized_variable_names[name + ":0"] = 1

    return (assignment_map, initialized_variable_names)


def model_fn_builder(value2field_config, init_checkpoint, learning_rate, num_train_steps, num_warmup_steps,
                     layer_indexes="-1,-2,-3,-4", use_tpu=False,
                     use_one_hot_embeddings=False):
    def model_fn(features, labels, mode, params):  # pylint: disable=unused-argument
        """The `model_fn` for TPUEstimator."""

        input_ids = features["input_ids"]
        input_shape = get_shape_list(input_ids, expected_rank=2)
        batch_size = input_shape[0]
        seq_length = input_shape[1]

        output_ids = features.get("output_ids", None)
        input_mask = features.get("input_mask", None)
        output_mask = features.get("output_mask", None)
        if input_mask is None:
            input_mask = tf.ones(shape=[batch_size, seq_length], dtype=tf.int32)
        if output_ids is None:
            output_ids = tf.ones(shape=[batch_size, seq_length], dtype=tf.int32)
        if output_mask is None:
            output_mask = tf.ones(shape=[batch_size, seq_length], dtype=tf.int32)

        is_training = (mode == tf.estimator.ModeKeys.TRAIN)
        (loss, output_embedding, input_embedding) = create_model(value2field_config,
                                                                 is_training,
                                                                 input_ids,
                                                                 input_mask, output_ids, output_mask)

        # init checkpoint
        tvars = tf.trainable_variables()
        initialized_variable_names = {}
        scaffold_fn = None
        if init_checkpoint:
            (assignment_map,
             initialized_variable_names) = get_assignment_map_from_checkpoint(
                tvars, init_checkpoint)
            # tf.logging.debug(tvars)
            tf.train.init_from_checkpoint(init_checkpoint, assignment_map)

        # tf.logging.info("**** Trainable Variables ****")
        # for var in tvars:
        #     init_string = ""
        #     if var.name in initialized_variable_names:
        #         init_string = ", *INIT_FROM_CKPT*"
        #     tf.logging.info("  name = %s, shape = %s%s", var.name, var.shape,
        #                     init_string)

        output_spec = None

        if mode == tf.estimator.ModeKeys.TRAIN:
            train_op = create_optimizer(
                loss, learning_rate, num_train_steps, num_warmup_steps, use_tpu)
            output_spec = tf.estimator.EstimatorSpec(
                mode=mode,
                loss=loss,
                train_op=train_op,
            )
        elif mode == tf.estimator.ModeKeys.EVAL:
            output_spec = tf.estimator.EstimatorSpec(
                mode=mode,
                loss=loss,
            )
        else:
            output_spec = tf.estimator.EstimatorSpec(
                mode=mode,
                export_outputs={"embedding": tf.estimator.export.PredictOutput({"embedding": input_embedding})},
                predictions={"output_embedding": output_embedding})
        return output_spec

    return model_fn


def serving_input_receiver_fn_builder(seq_length, batch_size):
    feature_spec = {"input_ids": tf.FixedLenFeature([seq_length], tf.int64)}

    # def serving_input_receiver_fn():
    #     input_ids = tf.placeholder(dtype=tf.int64,
    #                                shape=[ seq_length],
    #                                name='input_ids')
    #     # 表示post字段和tensor的对应关系
    #     receiver_tensors = {'input_ids': input_ids}
    #     # features = tf.parse_example(serialized_tf_example, feature_spec)
    #     return tf.estimator.export.ServingInputReceiver(receiver_tensors, receiver_tensors)
    input_ids = tf.placeholder(dtype=tf.int64,
                               shape=[1, seq_length],
                               name='input_ids')
    return tf.estimator.export.build_raw_serving_input_receiver_fn({'input_ids': input_ids})


def input_fn_builder(features_path, seq_length, is_training, drop_remainder):
    def input_fn(params):
        def parse(tfrecord):
            features = {"input_ids": tf.FixedLenFeature([seq_length], tf.int64),
                        "input_mask": tf.FixedLenFeature([seq_length], tf.int64),
                        "output_ids": tf.FixedLenFeature([seq_length], tf.int64),
                        "output_mask": tf.FixedLenFeature([seq_length], tf.int64)}
            data = tf.parse_single_example(tfrecord, features)
            return data, data["output_ids"]

        if is_training:
            batch_size = params['train_batch_size']
        else:
            batch_size = params['eval_batch_size']
        tf.logging.info(params)
        # for max_seq_length=32, train_batch_size=32, 12 G VRAM GPU
        # dataset = tf.data.TFRecordDataset(features_path).map(parse, num_parallel_calls=8)
        # if is_training:
        #     dataset = dataset.shuffle(buffer_size=100).repeat()
        # dataset = dataset.batch(batch_size=batch_size * 4, drop_remainder=drop_remainder).prefetch(
        #     batch_size * 4)
        dataset = tf.data.TFRecordDataset(features_path).map(parse, num_parallel_calls=16)
        if is_training:
            dataset = dataset.shuffle(buffer_size=batch_size * 16).repeat()
        dataset = dataset.batch(batch_size=batch_size, drop_remainder=drop_remainder).prefetch(
            batch_size * 16)
        return dataset

    return input_fn


def param_input_fn_builder(data, drop_remainder):
    def input_fn(params):
        batch_size = params['predict_batch_size']
        dataset = tf.data.Dataset.from_tensor_slices(data)
        dataset = dataset.batch(batch_size=batch_size, drop_remainder=drop_remainder).prefetch(
            batch_size * 16)
        return dataset

    return input_fn


class Setting:
    def __init__(self,
                 data_dir,
                 config_file,
                 vocab_file,
                 output_dir,
                 init_checkpoint=None,
                 do_lower_case=True,
                 max_seq_length=32,
                 train_batch_size=32,
                 eval_batch_size=8,
                 predict_batch_size=8,
                 learning_rate=1e-5,
                 num_train_epochs=4.0,
                 warmup_proportion=0.1,
                 save_checkpoints_steps=5000,
                 iterations_per_loop=1000,
                 tpu_name=None):
        """
        从bert模型源码修改得到，具体描述见bert的源码
        https://github.com/google-research/bert

        :param data_dir:
        :param config_file:
        :param vocab_file:
        :param output_dir:
        :param init_checkpoint:
        :param do_lower_case:
        :param max_seq_length:
        :param train_batch_size:
        :param eval_batch_size:
        :param predict_batch_size:
        :param learning_rate:
        :param num_train_epochs:
        :param warmup_proportion:
        :param save_checkpoints_steps:
        :param iterations_per_loop:
        :param tpu_name:
        """
        self.data_dir = data_dir
        self.config_file = config_file
        self.vocab_file = vocab_file
        self.output_dir = output_dir
        self.init_checkpoint = init_checkpoint
        self.do_lower_case = do_lower_case
        self.max_seq_length = max_seq_length
        self.train_batch_size = train_batch_size
        self.eval_batch_size = eval_batch_size
        self.predict_batch_size = predict_batch_size
        self.learning_rate = learning_rate
        self.num_train_epochs = num_train_epochs
        self.warmup_proportion = warmup_proportion
        self.save_checkpoints_steps = save_checkpoints_steps
        self.iterations_per_loop = iterations_per_loop
        self.tpu_name = tpu_name


def data_info(data_dir):
    with open(os.path.join(data_dir, "info.json")) as f:
        return json.load(f)


def load_global_step_from_checkpoint_dir(checkpoint_dir):
    try:
        checkpoint_reader = tf.train.NewCheckpointReader(
            tf.train.latest_checkpoint(checkpoint_dir))
        return checkpoint_reader.get_tensor(tf.GraphKeys.GLOBAL_STEP)
    except:  # pylint: disable=bare-except
        return 0


def train_val(setting):
    """
    训练并评估模型

    Args:
        setting (Setting):
    """
    config, data_size, run_config, steps_per_epoch = setup(setting)
    setting.save_checkpoints_steps = int(data_size["train"] / setting.train_batch_size)
    num_train_steps = int(
        data_size["train"] / setting.train_batch_size * setting.num_train_epochs)
    num_warmup_steps = int(num_train_steps * setting.warmup_proportion)
    train_input_fn = input_fn_builder(os.path.join(setting.data_dir, f"train_{setting.max_seq_length}.tfrecord"),
                                      seq_length=setting.max_seq_length, is_training=True, drop_remainder=True)
    if num_warmup_steps != 0:
        # warmup training
        tf.logging.info("***** Warmup training *****")
        tf.logging.info("  Num examples = %d", data_size["train"])
        tf.logging.info("  Batch size = %d", setting.train_batch_size)
        tf.logging.info("  Num steps = %d", num_warmup_steps)
        model_fn = model_fn_builder(layer_indexes="-1,-2,-3,-4", value2field_config=config,
                                    init_checkpoint=setting.init_checkpoint,
                                    learning_rate=setting.learning_rate,
                                    num_train_steps=num_warmup_steps,
                                    num_warmup_steps=num_warmup_steps,
                                    )
        estimator = tf.estimator.Estimator(
            model_fn=model_fn,
            config=run_config,
            model_dir=setting.output_dir,
            params=dict(train_batch_size=setting.train_batch_size,
                        eval_batch_size=setting.eval_batch_size,
                        predict_batch_size=setting.predict_batch_size))

        estimator.train(input_fn=train_input_fn, max_steps=num_warmup_steps)
        num_train_steps = num_train_steps - num_warmup_steps
        num_warmup_steps = 0

    model_fn = model_fn_builder(layer_indexes="-1,-2,-3,-4", value2field_config=config,
                                init_checkpoint=None,
                                learning_rate=setting.learning_rate,
                                num_train_steps=num_train_steps,
                                num_warmup_steps=num_warmup_steps)
    estimator = tf.estimator.Estimator(
        model_fn=model_fn,
        config=run_config,
        model_dir=setting.output_dir,
        params=dict(train_batch_size=setting.train_batch_size,
                    eval_batch_size=setting.eval_batch_size,
                    predict_batch_size=setting.predict_batch_size)
    )
    # setup for training
    train_spec = tf.estimator.TrainSpec(input_fn=train_input_fn, max_steps=num_train_steps)
    # setup for eval
    eval_steps = None
    eval_drop_remainder = False
    eval_input_fn = input_fn_builder(os.path.join(setting.data_dir, f"val_{setting.max_seq_length}.tfrecord"),
                                     seq_length=setting.max_seq_length, is_training=False,
                                     drop_remainder=eval_drop_remainder)
    eval_spec = tf.estimator.EvalSpec(input_fn=eval_input_fn, steps=eval_steps)
    tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)


def setup(setting):
    data_size = data_info(setting.data_dir)
    tf.summary.FileWriterCache.clear()
    config = ValueConfig.from_json_file(setting.config_file)
    tf.gfile.MakeDirs(setting.output_dir)
    steps_per_epoch = data_size["train"] // setting.train_batch_size
    run_config = tf.estimator.RunConfig(
        save_checkpoints_steps=setting.save_checkpoints_steps,
        # session_config=tf.ConfigProto(device_count = {'GPU': 0})
    )

    return config, data_size, run_config, steps_per_epoch


def load_fields(path=r"J:\nlptest\res\data\fields.json"):
    with open(path) as f:
        fields = json.load(f)
    return fields


def export(setting):
    """
    导出模型
    Args:
        setting (Setting):

    Returns:

    """
    config, data_size, run_config, steps_per_epoch = setup(setting)
    num_train_steps = int(
        data_size["train"] / setting.train_batch_size * setting.num_train_epochs)
    num_warmup_steps = int(num_train_steps * setting.warmup_proportion)
    model_fn = model_fn_builder(layer_indexes="-1,-2,-3,-4", value2field_config=config,
                                init_checkpoint=setting.init_checkpoint,
                                learning_rate=setting.learning_rate,
                                num_train_steps=num_train_steps,
                                num_warmup_steps=num_warmup_steps)
    estimator = tf.estimator.Estimator(
        model_fn=model_fn,
        config=run_config,
        model_dir=setting.output_dir,
        params=dict(train_batch_size=setting.train_batch_size,
                    eval_batch_size=setting.eval_batch_size,
                    predict_batch_size=setting.predict_batch_size))
    save_hook = tf.train.CheckpointSaverHook(setting.output_dir, save_secs=1)
    print(list(estimator.predict(
        input_fn=param_input_fn_builder(data={"input_ids": np.random.randint(21128, size=[9, setting.max_seq_length])},
                                        drop_remainder=False), hooks=[save_hook])))
    estimator.export_savedmodel(setting.output_dir,
                                serving_input_receiver_fn_builder(setting.max_seq_length, setting.predict_batch_size),
                                strip_default_attrs=True)
