from __future__ import print_function
import tensorflow as tf
import numpy as np
import lib.test_inputs as test_inputs

"""Load model from export_dir, predict on input data, expected output is 2,2,3."""
export_dir = './tmp/'
checkpoint_path = tf.train.latest_checkpoint(export_dir)
saver = tf.train.import_meta_graph(checkpoint_path + ".meta", import_scope=None)

def load_graph():
    ret_list = []
    with tf.Session() as sess:
        saver.restore(sess, checkpoint_path)
        output = sess.run("predict/prediction:0", feed_dict={"predict/X:0": test_inputs.in_data})
        for i in output:
            ret_list.append(np.asscalar(i))
    return ret_list

def rate(arr):
    rating = -1
    with tf.Session() as sess:
        saver.restore(sess, checkpoint_path)
        output = sess.run("predict/prediction:0", feed_dict={"predict/X:0": [arr]})
        rating = np.asscalar(output[0])
    return str(rating)

if __name__ == '__main__':
    print(rate(test_inputs.in_data[0]))