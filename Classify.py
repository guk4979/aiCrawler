import numpy as np
from keras import utils
import matplotlib.pyplot as plt
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import RMSprop
import tensorflow as tf
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import os
from PIL import Image
import Rule

# local_zip = '/tmp/cats_and_dogs_filtered.zip'

# zip_ref = zipfile.ZipFile(local_zip, 'r')

# zip_ref.extractall('/tmp')
# zip_ref.close()

base_dir = './CorrectImages'

train_dir = base_dir
train_cat_dir = os.path.join(base_dir, Rule.keyword)
validation_dir = os.path.join(base_dir, 'validation')

# 훈련에 사용되는 고양이/개 이미지 경로
# train_dogs_dir = os.path.join(train_dir, 'dogs')
print(train_cat_dir)
# print(train_dogs_dir)

# 테스트에 사용되는 고양이/개 이미지 경로
# validation_cats_dir = os.path.join(validation_dir, 'cats')
# validation_dogs_dir = os.path.join(validation_dir, 'dogs')
# print(validation_cats_dir)
# print(validation_dogs_dir)
train_fnames = os.listdir( train_cat_dir )
# train_dog_fnames = os.listdir( train_dogs_dir )

print(train_fnames[:5])
# print(train_dog_fnames[:5])

print('Total training cat images :', len(os.listdir(train_cat_dir)))
# print('Total training dog images :', len(os.listdir(train_dogs_dir)))

# print('Total validation cat images :', len(os.listdir(validation_cats_dir)))
# print('Total validation dog images :', len(os.listdir(validation_dogs_dir)))


nrows, ncols = 4, 4
pic_index = 0

fig = plt.gcf()
fig.set_size_inches(ncols*3, nrows*3)

pic_index+=8

next_cat_pix = [os.path.join(train_cat_dir, fname)
                for fname in train_fnames[ pic_index-8:pic_index]]

# next_dog_pix = [os.path.join(train_dogs_dir, fname)
#                 for fname in train_dog_fnames[ pic_index-8:pic_index]]

for i, img_path in enumerate(next_cat_pix):
  sp = plt.subplot(nrows, ncols, i + 1)
  sp.axis('Off')

  img = mpimg.imread(img_path)
  plt.imshow(img)

plt.show()


model = tf.keras.models.Sequential([
  tf.keras.layers.Conv2D(16, (3,3), activation='relu', input_shape=(150, 150, 3)),
  tf.keras.layers.MaxPooling2D(2,2),
  tf.keras.layers.Conv2D(32, (3,3), activation='relu'),
  tf.keras.layers.MaxPooling2D(2,2),
  tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
  tf.keras.layers.MaxPooling2D(2,2),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(512, activation='relu'),
  tf.keras.layers.Dense(1, activation='sigmoid')
])

model.summary()

model.compile(optimizer=RMSprop(lr=0.001),
            loss='binary_crossentropy',
            metrics = ['accuracy'])



train_datagen = ImageDataGenerator( rescale = 1.0/255. )
test_datagen  = ImageDataGenerator( rescale = 1.0/255. ) #ImageDataGenerator(horizontal_flip=True, vertical_flip=True, rescale=1/255.0, rotation_range=0.45,zoom_range=[0.5, 1.5])

train_generator = train_datagen.flow_from_directory(train_dir,
                                                  batch_size=20,
                                                  class_mode='binary',
                                                  target_size=(150, 150))
validation_generator =  test_datagen.flow_from_directory(train_dir,
                                                       batch_size=20,
                                                       class_mode  = 'binary',
                                                       target_size = (150, 150))

history = model.fit(train_generator,
                    validation_data=validation_generator,
                    steps_per_epoch=3,
                    epochs=20,
                    validation_steps=20,
                    verbose=2)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(acc))

plt.plot(epochs, acc, 'bo', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend()

plt.figure()

plt.plot(epochs, loss, 'go', label='Training Loss')
plt.plot(epochs, val_loss, 'g', label='Validation Loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()


img=utils.load_img("./test.jpg", target_size=(150, 150))
x=utils.img_to_array(img)
x=np.expand_dims(x, axis=0)
images = np.vstack([x])

classes = model.predict(images, batch_size=10)
print(classes[0])
