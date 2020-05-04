import tensorflow as tf

class Fasttext:
    def __init__(self,sequence_length,num_classes,vocab_size,embedding_size,
                 l2_reg_lambda=0.0):

        # Placeholders for input, output and dropout
        self.input_x = tf.placeholder(tf.int32, [None, sequence_length], name="input_x")
        self.input_y = tf.placeholder(tf.float32, [None, num_classes], name="input_y")
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")

        # Keeping track of l2 regularization loss (optional)
        l2_loss = tf.constant(0.0)

        # Embedding layer
        with tf.name_scope("embedding"):
            self.W = tf.Variable(
                tf.random_uniform([vocab_size, embedding_size], -1.0, 1.0),
                name="emb_W")
            self.embedded_chars = tf.nn.embedding_lookup(self.W, self.input_x)  # [None,sequence_length,embedding_size]

        # Create a average layer (avg pooling)
        with tf.name_scope("average"):
            self.mean_sentence = tf.reduce_mean(self.embedded_chars, axis=1)          # [None,embedding_size]

        # Add dropout
        with tf.name_scope("dropout"):
            self.h_drop = tf.nn.dropout(self.mean_sentence, self.dropout_keep_prob)

        # Final (unnormalized) scores and predictions
        with tf.name_scope("output"):
            W = tf.Variable(tf.truncated_normal(shape=[embedding_size, num_classes], stddev=0.1),name='W')
            b = tf.Variable(tf.truncated_normal(shape=[num_classes]),name='b')

            l2_loss += tf.nn.l2_loss(W)
            l2_loss += tf.nn.l2_loss(b)
            self.scores = tf.nn.xw_plus_b(self.h_drop, W, b, name="scores")
            self.predictions = tf.argmax(self.scores, 1, name="predictions")

        # Calculate mean cross-entropy loss
        with tf.name_scope("loss"):
            losses = tf.nn.softmax_cross_entropy_with_logits(logits=self.scores, labels=self.input_y)
            self.loss = tf.reduce_mean(losses) + l2_reg_lambda * l2_loss

        # Accuracy
        with tf.name_scope("accuracy"):
            correct_predictions = tf.equal(self.predictions, tf.argmax(self.input_y, 1))
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, "float"), name="accuracy")


# model = Fasttext(sequence_length=params['sequence_length'],
#                     num_classes=params['num_classes'],
#                     vocab_size=params['vocab_size'],
#                     embedding_size=params['embedding_size'],
#                     l2_reg_lambda=params['l2_reg_lambda'])