# Import the libraries
import os
from keras import utils
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.models import Model
from keras.layers import Concatenate
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import Rule
from multiprocessing import Pool
import shutil

class FeatureExtractor:
  def __init__(self):
      # Use VGG-16 as the architecture and ImageNet for the weight
      base_model = VGG16(weights='imagenet')
      # Customize the model to return features from fully-connected layer
      self.model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

  def extract(self, img):
      # Resize the image
      img = img.resize((224, 224))
      # Convert the image color space
      img = img.convert('RGB')
      # Reformat the image
      x = utils.img_to_array(img)
      x = np.expand_dims(x, axis=0)
      x = preprocess_input(x)
      # Extract Features
      feature = self.model.predict(x)[0]
      return feature / np.linalg.norm(feature)

# def saveImgFeature(img_path):
#   try:
#     # Extract Features
#     fe = FeatureExtractor()
#     feature = fe.extract(img=Image.open(img_path))

#     # return feature

#     # Save the Numpy array (.npy) on designated path
#     feature_path = "./features/" + str(i) + ".npy"
#     np.save(feature_path, feature)
#   except Exception as e:
#     print('예외가 발생했습니다.', e)

def classify():

  features = []
  querys = []
  cor_base_dir = "./CorrectImages"
  incor_base_dir = "./IncorrectImages"
  cor_feature_dir = "./features/CorrectImages"
  incor_feature_dir = "./features/IncorrectImages"
  correct_dir = os.path.join(cor_base_dir, Rule.keyword)
  correct_img = os.listdir(correct_dir)
  correct_feature_dir = os.path.join(cor_feature_dir, Rule.keyword)
  correctimg_paths = []
  incorrect_dir = os.path.join(incor_base_dir, Rule.keyword)
  incorrect_img = os.listdir(incorrect_dir)
  incorrect_feature_dir = os.path.join(incor_feature_dir, Rule.keyword)
  incorrectimg_paths = []

  # Save Image Feature Vector with Database Images
  # fe = FeatureExtractor()

  for img in correct_img:
    image_path = os.path.join(correct_dir, img)
    correctimg_paths.append(image_path)

  for img in incorrect_img:
    image_path = os.path.join(incorrect_dir, img)
    incorrectimg_paths.append(image_path)

  #이미지 feature 가져오기
  for i in os.listdir(incorrect_feature_dir):
    feature = np.load(os.path.join(incorrect_feature_dir, i))
    features.append(feature)

  for i in os.listdir(correct_feature_dir):
    feature = np.load(os.path.join(correct_feature_dir, i))
    querys.append(feature)

  # Insert the image query
  # for i in os.listdir(correct_img):
  #   img = Image.open(.format(i))
  #   query = fe.extract(img)
  #   querys.append(query)

  # query = Concatenate()([query1, query2]).numpy()
  # print(query)


  # Calculate the similarity (distance) between images
  value = features - querys[0]
  for i in range(len(querys)-1):
    value += features - querys[i+1]
  value = value / len(querys)

  dists = np.linalg.norm(value, axis=1)

  ids = np.argsort(dists)

  scores = [(dists[id], incorrectimg_paths[id]) for id in ids]

  # Visualize the result
  # axes=[]
  # fig=plt.figure(figsize=(10,20))
  # for a in range(len(scores)):
  #     score = scores[a]
  #     axes.append(fig.add_subplot(10, 20, a+1))
  #     subplot_title=str(round(score[0],2)) + "/m" + str(score[2]+1)
  #     axes[-1].set_title(subplot_title)  
  #     plt.axis('off')
  #     plt.imshow(Image.open(score[1]))
  # fig.tight_layout()
  # plt.show()

  for a in range(len(scores)):
    score = scores[a]
    img_name = score[1]
    img_name = int(img_name[:-4].replace("./IncorrectImages\\{}\\".format(Rule.keyword), ""))
    fe_name = img_name
    fe_path = os.path.join("./features/IncorrectImages/{}/{}.npy".format(Rule.keyword, fe_name))
    if score[0] <= 0.95:
      new_name = avoidDuplication()
      shutil.move(score[1], "./CorrectImages/{}/{}.jpg".format(Rule.keyword, new_name))
      shutil.move(fe_path, "./features/CorrectImages/{}/{}.npy".format(Rule.keyword, new_name))
      if os.path.exists(fe_path):
        os.path.remove(fe_path)
  
  # shutil.rmtree("./IncorrectImages/{}".format(Rule.keyword))
  # shutil.rmtree("./features/IncorrectImages/{}".format(Rule.keyword))

def avoidDuplication():
  i = 0
  while os.path.exists("./CorrectImages/{}/{}.jpg".format(Rule.keyword, str(i))) & os.path.exists("./features/CorrectImages/{}/{}.npy".format(Rule.keyword, str(i))):
    i += 1
  return i

if __name__ == "__main__":
  classify()