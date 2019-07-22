import tensorflow as tf
import matplotlib.pyplot as plt

mnist = tf.keras.datasets.mnist  # 28x28 images of these hand-written digits
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# plt.imshow(x_train[0])
plt.imshow(x_train[0], cmap=plt.cm.binary)  # 黑白
plt.show()
