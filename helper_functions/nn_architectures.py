import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, Model, regularizers
import numpy as np

def nn1():
    input1 = layers.Input(shape=(18, 18))
    input2 = layers.Input(shape=(18, 18))

    flatten1 = layers.Flatten()(input1)
    flatten2 = layers.Flatten()(input2)

    concat = layers.Concatenate()([flatten1, flatten2])
    dense1 = layers.Dense(200, activation='relu')(concat)
    dense2 = layers.Dense(100, activation='relu')(dense1)

    output1 = layers.Dense(201, activation='softmax', name='output1')(dense2)  # Adjust output dimension to match the range (150 - 50 + 1)
    output2 = layers.Dense(201, activation='softmax', name='output2')(dense2)  # Adjust output dimension to match the range (150 - 50 + 1)

    model = Model(inputs=[input1, input2], outputs=[output1, output2])
    return model

# Define your training function
def train_model(model_function, matrixA_list, matrixB_list, output_tuple_list, epochs=10, batch_size=32, verbose=False):
    # Convert DataFrame to numpy arrays
    matrixA_array = np.array(matrixA_list)
    matrixB_array = np.array(matrixB_list)
    output_array = np.array(output_tuple_list)
    
    # Build the model
    model = model_function()

    # Compile the model
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit([matrixA_array, matrixB_array], [output_array[:, 0], output_array[:, 1]], epochs=epochs, batch_size=batch_size, verbose=verbose)
    return model

def nn2():
    input1 = layers.Input(shape=(18, 18))
    input2 = layers.Input(shape=(18, 18))

    flatten1 = layers.Flatten()(input1)
    flatten2 = layers.Flatten()(input2)

    concat = layers.Concatenate()([flatten1, flatten2])
    
    # Wide sparse layers with L1 regularization
    dense1 = layers.Dense(512, activation='relu', kernel_regularizer=regularizers.l1(0.01))(concat)
    dropout1 = layers.Dropout(0.5)(dense1)
    
    dense2 = layers.Dense(256, activation='sigmoid', kernel_regularizer=regularizers.l1(0.01))(dropout1)
    dropout2 = layers.Dropout(0.5)(dense2)

    output1 = layers.Dense(201, activation='softmax', name='output1')(dropout2)  # Adjust output dimension to match the range (150 - 50 + 1)
    output2 = layers.Dense(201, activation='softmax', name='output2')(dropout2)  # Adjust output dimension to match the range (150 - 50 + 1)

    model = Model(inputs=[input1, input2], outputs=[output1, output2])
    return model

def nn3():
    input1 = layers.Input(shape=(18, 18))
    input2 = layers.Input(shape=(18, 18))

    flatten1 = layers.Flatten()(input1)
    flatten2 = layers.Flatten()(input2)

    concat = layers.Concatenate()([flatten1, flatten2])
    dense1 = layers.Dense(69, activation='relu')(concat)
    dense2 = layers.Dense(6969, activation='relu')(dense1)
    dense3 = layers.Dense(123, activation='relu')(concat)




    output1 = layers.Dense(201, activation='softmax', name='output1')(dense2)  # Adjust output dimension to match the range (150 - 50 + 1)
    output2 = layers.Dense(201, activation='softmax', name='output2')(dense2)  # Adjust output dimension to match the range (150 - 50 + 1)

    model = Model(inputs=[input1, input2], outputs=[output1, output2])
    return model

def nn4():
    input1 = layers.Input(shape=(18, 18))
    input2 = layers.Input(shape=(18, 18))

    flatten1 = layers.Flatten()(input1)
    flatten2 = layers.Flatten()(input2)

    concat = layers.Concatenate()([flatten1, flatten2])
    dense1 = layers.Dense(2048, activation='sigmoid')(concat)
    dense2 = layers.Dense(128, activation='sigmoid')(dense1)
    dense3 = layers.Dense(256, activation='relu')(dense2)


    output1 = layers.Dense(201, activation='softmax', name='output1')(dense3)  # Adjust output dimension to match the range (150 - 50 + 1)
    output2 = layers.Dense(201, activation='softmax', name='output2')(dense3)  # Adjust output dimension to match the range (150 - 50 + 1)

    model = Model(inputs=[input1, input2], outputs=[output1, output2])
    return model

def nn5():
    input1 = layers.Input(shape=(18, 18))
    input2 = layers.Input(shape=(18, 18))

    flatten1 = layers.Flatten()(input1)
    flatten2 = layers.Flatten()(input2)

    concat = layers.Concatenate()([flatten1, flatten2])
    dense1 = layers.Dense(2048, activation='sigmoid')(concat)
    dense2 = layers.Dense(128, activation='sigmoid')(dense1)
    dense3 = layers.Dense(256, activation='relu')(dense2)
    dense4 = layers.Dense(500, activation='sigmoid')(dense3)
    dense5 = layers.Dense(100, activation='relu')(dense4)
    dense6 = layers.Dense(256, activation='sigmoid')(dense5)
    dense7 = layers.Dense(256, activation='relu')(dense6)
    dense8 = layers.Dense(64, activation='sigmoid')(dense7)
    dense9 = layers.Dense(32, activation='relu')(dense8)
    dense10 = layers.Dense(128, activation='sigmoid')(dense9)
    dense11 = layers.Dense(256, activation='relu')(dense10)


    output1 = layers.Dense(201, activation='softmax', name='output1')(dense11)  # Adjust output dimension to match the range (150 - 50 + 1)
    output2 = layers.Dense(201, activation='softmax', name='output2')(dense11)  # Adjust output dimension to match the range (150 - 50 + 1)

    model = Model(inputs=[input1, input2], outputs=[output1, output2])
    return model