# -*- coding: utf-8 -*-
"""Project AI Fire detection

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1H-judiPC1y_TKNxHeP8vqwWEK7rUv1mH
"""

# Commented out IPython magic to ensure Python compatibility.
# import libraries packages 
import shutil
import tensorflow as tf
import keras_preprocessing
from keras_preprocessing import image
from keras_preprocessing.image import ImageDataGenerator
import shutil
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input, Dropout
# %matplotlib inline
import matplotlib.pyplot as plt
import numpy as np #To allows for a user to upload a image, Means it will prompt you to select a file. Click on “Choose Files” then select and upload the file.
from google.colab import files #To upload from local drive
from keras.preprocessing import image #Use this library to converting an image with the Keras API

# To download files from URL
!wget https://github.com/DeepQuestAI/Fire-Smoke-Dataset/releases/download/v1/FIRE-SMOKE-DATASET.zip 
# To decompress 
!unzip FIRE-SMOKE-DATASET.zip

import shutil
shutil.rmtree('/content/FIRE-SMOKE-DATASET/Test/Smoke')
shutil.rmtree('/content/FIRE-SMOKE-DATASET/Train/Smoke')

TRAINING_DIR = "/content/FIRE-SMOKE-DATASET/Train"

#This is the technique used to produce many different converted copies of the same original images.
#All versions will be different in other respects depending on the enhancement techniques we will use below.
#We will provide a new perspective to capture the object in real life.
training_datagen = ImageDataGenerator(rescale=1./255, #the parameter rescale  to multiply every pixel in the preprocessing  1./255 ,need this before training neural network
                                     
                                      #To existing images are flipped, zoomed  to add more training on the data and avoid over-fitting.
                                      #used Zoom
                                      zoom_range=0.15,# zoom.
                                      #flipping
                                      #To get a better result, we use image flipping, which is a great magnification technique.
                                      #It makes sense to use it with a lot of different objects.
                                      horizontal_flip=True, # horizontal flip.
                                      #use the fill_mode argument.
                                      #the default value used is “nearest” which simply replaces the empty area with the nearest pixel values.
                                      fill_mode='nearest')

#directory 
#path to the folder that contains all the images.
VALIDATION_DIR = "/content/FIRE-SMOKE-DATASET/Test"
validation_datagen = ImageDataGenerator(rescale = 1./255)#the parameter rescale  to multiply every pixel in the preprocessing  1./255 ,need this before training neural network

# ImageDataGenerator flow_from_directory
# to read the images directly from the directory and augment them while the neural network model is learning on the training data.
# The method expects that images belonging to different classes are present in different folders but are inside the same folder. 
train_generator = training_datagen.flow_from_directory(
  TRAINING_DIR,
  #resize to this size
  target_size=(224,224), # To a resizes all the images to the size of 224X224, irrespective of the original size of the image present in train directory.
  #shuffle the data 
  #default: True
  #split the data randomly
  shuffle = True,
  # classes to predict
  class_mode='categorical', #Set categorical to 2-D one-hot encoded labels.
  # number of images to extract from folder for every batch
  batch_size = 128 #Size of the batches of data.
)

# ImageDataGenerator flow_from_directory
validation_generator = validation_datagen.flow_from_directory(
  VALIDATION_DIR,
  target_size=(224,224), # To a resizes all the images to the size of 224X224, irrespective of the original size of the image present in validation directory.
  # classes to predict
  class_mode='categorical',#Set categorical to 2-D one-hot encoded labels.
  #shuffle the data 
  #default: True
  #split the data randomly
  shuffle = True,
  # number of images to extract from folder for every batch
  batch_size= 14 #Size of the batches of data.
)

# use this code to classify input images that have class labels inside ImageNet
# shape should use for the input for keras
input_tensor = Input(shape=(224, 224, 3))
# create the base pre-trained model
base_model = InceptionV3(input_tensor=input_tensor, weights='imagenet', include_top=False)

# add a global spatial average pooling layer
x = base_model.output
x = GlobalAveragePooling2D()(x)
# let's add a fully-connected layer,for CNN,ReLu is treated as a standard activation function
x = Dense(2048, activation='relu')(x)
# Add a dropout rate of 0.25.Dropout is a technique where randomly selected neurons are ignored during training.
x = Dropout(0.25)(x)
x = Dense(1024, activation='relu')(x)
x = Dropout(0.2)(x)
# and a logistic layer -- let's say we have 2 classes
predictions = Dense(2, activation='softmax')(x)
# this is the model we will train
model = Model(inputs=base_model.input, outputs=predictions)

# first: train only the top layers (which were randomly initialized)
# freeze all complex InceptionV3 layers
for layer in base_model.layers:
    layer.trainable = False

# compile the model using selected loss function, optimizer and metrics,RMSProp is designed to accelerate the optimization process
model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['acc'])

#Implement callback function to stop training.
class myCallback(tf.keras.callbacks.Callback):
#End epoch {} of training
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('val_loss')<=0.1099 and logs.get('loss')<=0.1099):
      print('\n\n Reached The Destination!')

      self.model.stop_training = True
# create a callback object
callbacks = myCallback()

# Fit model on training data
#pass some validation for
    # monitoring validation loss and metrics
    # at the end of each epoch

history = model.fit(
    train_generator,
    steps_per_epoch = 14,
    epochs = 20,
    validation_data = validation_generator,
    validation_steps = 14,
    callbacks=[callbacks]
)

# Unfreeze some layers in our model
for layer in model.layers[:249]:
   layer.trainable = False
for layer in model.layers[249:]:
   layer.trainable = True
#import package stochastic gradient descent(SGD) 
from tensorflow.keras.optimizers import SGD
# Train model with more trainable layers
model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['acc']) 
#Implement callback function to stop training.
class myCallback(tf.keras.callbacks.Callback):
#End epoch {} of training
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('val_loss')<=0.1099 and logs.get('loss')<=0.1099):
      print('\n\n Reached The Destination!')
      self.model.stop_training = True
# create a callback object
callbacks = myCallback()

# Fit model on training data
#pass some validation for
    # monitoring validation loss and metrics
    # at the end of each epoch

history = model.fit(
    train_generator,
    steps_per_epoch = 14,
    epochs = 10,
    validation_data = validation_generator,
    validation_steps = 14,
    callbacks=[callbacks]
)
#Number of layers after calling the model

print(len(base_model.layers))

#Retrieve a list of list results on training and test data
# sets for each training epoch
acc = history.history['acc']
val_acc = history.history['val_acc']
loss = history.history['loss']
val_loss = history.history['val_loss']
# Get number of epochs
epochs = range(len(acc))
#Plot training and validation accuracy per epoch, name lable and color
plt.plot(epochs, acc, 'g', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
#Used to Place a legend on the axes also,Loc in legend() is used to specify the location of the legend, default value of loc is loc=”best” (upper left)
plt.legend(loc=0)
#Show figure for training and validation accuracy
plt.figure()
plt.show()
# Plot training and validation loss per epoch,name lable and color
plt.plot(epochs, loss, 'r', label='Training loss')
plt.plot(epochs, val_loss, 'orange', label='Validation loss')
plt.title('Training and validation loss')
#Used to Place a legend on the axes also,Loc in legend() is used to specify the location of the legend, default value of loc is loc=”best” (upper left)

plt.legend(loc=0)
#Show figure for training and validation loss

plt.figure()
plt.show()

#predicting any random image
import numpy as np #To allows for a user to upload a image, Means it will prompt you to select a file. Click on “Choose Files” then select and upload the file.
from google.colab import files #To upload from local drive
#from keras.preprocessing import image #Use this library to converting an image with the Keras API
import keras.utils as image
#upload test images
uploaded = files.upload()
for fn in uploaded.keys():
  path = '/content/' + fn
# load_img function for loading an image from file as a PIL image object. PIL let saving many different image file formats.
  img = image.load_img(path, target_size=(224, 224))
#convert to numpy array
  x = image.img_to_array(img)
#Function used to expand the shape of an array. 
  x = np.expand_dims(x, axis=0) /255
  classes = model.predict(x)
# Indices of Max element
  print(np.argmax(classes[0])==0, max(classes[0]))