"""
建立神经网络模型 应用CNN
"""
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.callbacks import TensorBoard
import numpy as np
import os
import random

model = Sequential()
# 增加隐藏卷积层
model.add(Conv2D(32, (3, 3), padding='same',  # 32 Features , windows 3*3
                 input_shape=(176, 200, 3),
                 activation='relu'))
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

model.add(Conv2D(64, (3, 3), padding='same',
                 activation='relu'))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

model.add(Conv2D(128, (3, 3), padding='same',
                 activation='relu'))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

# 全连接层
model.add(Flatten())
model.add(Dense(512, activation='relu'))
model.add(Dropout(0.5))

# 输出层
model.add(Dense(4, activation='softmax'))

# 设置基础参数
learning_rate = 0.0001
opt = keras.optimizers.adam(lr=learning_rate, decay=1e-6)

model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

# 记录日志
tensorboard = TensorBoard(log_dir="logs/stage1")
