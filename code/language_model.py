from numpy import array
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Embedding,Dropout
import random

path = 'path to your corpus'
data = open(path, encoding='utf-8').read()

# 训练预料
# data = """ jack and Jill went up the hill?\n
# 		To fetch a pail of water?\n
# 		jack fell down and broke his crown.\n
# 		And, Jill came tumbling after.\n """

# prepare the tokenizer on the source text
tokenizer = Tokenizer()
tokenizer.fit_on_texts([data])

# 词典大小
vocab_size = len(tokenizer.word_index) + 1
print('Vocabulary Size: %d' % vocab_size)
# print(tokenizer.word_index)

data = data.split('\n')
sequences = list()
for item in data:
    encoded = tokenizer.texts_to_sequences([item])[0]
    if len(encoded) >= 3:
        sequences.append(encoded)
max_length = max(len(seq) for seq in sequences)
print(max_length)

# define model
model = Sequential()
model.add(Embedding(vocab_size, 10, input_length=max_length - 1))  # 参数：词汇量，embed_size, seq长度
model.add(LSTM(128, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(128, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(128))
model.add(Dropout(0.2))
model.add(Dense(vocab_size, activation='softmax'))
print(model.summary())
# compile network
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
try:
    model.load_weights('language.h5')
except Exception as e:
    print(e)
    pass


def MakeBatch(batch_size, sequences, max_length):
    # create line-based sequences
    sample_sequences = []
    for ii in sequences:
        if len(ii) == max_length:
            sample_sequences.append(ii)
            break
    sample_data = random.sample(sequences, batch_size - 1)
    for item in sample_data:
        i = random.randint(1, len(item) - 1)
        sample_sequences.append(item[:i + 1])
    sample_sequences = pad_sequences(sample_sequences, maxlen=max_length, padding='pre')
    sample_sequences = array(sample_sequences)
    X, y = sample_sequences[:, :-1], sample_sequences[:, -1]  # 将每个seq的最后一个元素拿出来，作为y
    y = to_categorical(y, num_classes=vocab_size)
    return X, y


def Gen(batch_size):
    while True:
        yield MakeBatch(batch_size, sequences, max_length)


# MakeBatch(256, sequences, max_length)
# model.fit(X, y, epochs=500, verbose=1)
if __name__ == '__main__':
    # fit network
    batch_size = 32
    gen = Gen(batch_size)
    model.fit_generator(gen, steps_per_epoch=100, epochs=500, verbose=1)
    model.save('language.h5')
