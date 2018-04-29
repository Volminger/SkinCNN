# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys

import numpy as np
import tensorflow as tf

from os import walk
from sklearn.metrics import roc_curve, auc
from PIL import Image
import math
from random import randint


import matplotlib.pyplot as plt

benignLes = ["DERMAL TUMOR BENIGN", "EPIDERMAL TUMOR BENIGN-BUCKET", "EPIDERMAL TUMOR BENIGN BUCKET", "Nevus", "PIGMENTED LESION BENIGN-BUCKET", "PIGMENTED LESION BENIGN BUCKET", "Rosacea Rhinophyma And Variants", "Seborrheic Keratosis", "Seborrheic Keratosis-BUCKET", "Seborrheic Keratosis BUCKET"]
nonNeoplasticLes = ["Acne Folliculitis Hidradenitis And Diseases Of Appendegeal Structures-BUCKET", "Acne Folliculitis Hidradenitis And Diseases Of Appendegeal Structures BUCKET", "Acne Vulgaris", "Eczema Spongiotic Dermatitis", "INFLAMMATORY-BUCKET", "INFLAMMATORY BUCKET", "Psoriasis Pityriasis Rubra Pilaris And Papulosquamous Disorders"]
malignantLes = ["malignant","Basal Cell Carcinoma", "EPIDERMAL TUMOR MALIGNANT-BUCKET", "EPIDERMAL TUMOR MALIGNANT BUCKET", "Melanoma", "PIGMENTED LESION MALIGNANT-BUCKET", "PIGMENTED LESION MALIGNANT BUCKET"]
upperCaseBenignLes = [x.upper() for x in benignLes]
upperCaseNonNeoplasticLes = [x.upper() for x in nonNeoplasticLes]
upperCaseMalignantLes = [x.upper() for x in malignantLes]

def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph

def getLesClass(lesName):
    if lesName.upper() in upperCaseBenignLes:
        return "Benign"
    elif lesName.upper() in upperCaseNonNeoplasticLes:
        return "nonNeoplastic"
    elif lesName.upper() in upperCaseMalignantLes:
        return "malignant"
    return "Les not found"

def getProbScoreForClass(className, benProp, nonProp, malProp):
    if className is "Benign":
        return benProp
    elif className is "nonNeoplastic":
        return nonProp
    elif className is "malignant":
        return malProp
    return -1

def getMaxProb(benProp, nonProp, malProp):
    listProb = [benProp, nonProp, malProp]
    return max(listProb)

def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):

    im = Image.open(file_name)

    size = 299,299
    width, height = im.size
    rotatedImagePillow = im.rotate(randint(0,359))
    radius = min(width, height)/2
    offset = int(radius * math.sqrt(2) / 2)
    startPoint = np.array([int(height/2 - offset), int(width/2 - offset)])
    croppedImagePillow = rotatedImagePillow.crop((startPoint[1], startPoint[0] , startPoint[1] + offset*2 , startPoint[0] + offset*2))
    randomNumber = randint(0,1)
    if randomNumber > 0.5:
     flippedImagePillow =  croppedImagePillow.transpose(Image.FLIP_TOP_BOTTOM)
    else:
     flippedImagePillow = croppedImagePillow.rotate(0)
    resizedImagePillow = flippedImagePillow.resize([299,299], Image.ANTIALIAS)

    resizedImagePillow.save('Validation.jpeg')
    im.close()
    rotatedImagePillow.close()
    croppedImagePillow.close()
    flippedImagePillow.close()
    resizedImagePillow.close()


    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.read_file('Validation.jpeg', input_name)
    if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(file_reader, channels=3, name="png_reader")
    elif file_name.endswith(".gif"):
        image_reader = tf.squeeze(tf.image.decode_gif(file_reader, name="gif_reader"))
    elif file_name.endswith(".bmp"):
        image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
    else:
        image_reader = tf.image.decode_jpeg(
        file_reader, channels=3, name="jpeg_reader")
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)

    return result


def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label


def getValidationAcc(test_path, sess, label_file):
    input_height = 299
    input_width = 299
    input_mean = 0
    input_std = 255
    input_layer = "input"
    output_layer = "InceptionV3/Predictions/Reshape_1"

    labels = load_labels(label_file)

    score = 0

    f = []
    for (dirpath, dirnames, filenames) in walk(test_path):
        print(dirpath)
        print(dirnames)
        f.append([dirpath,filenames])

    for file_ in f:
        # numberOfPredictedDiseases.append([0,0,0,0,0,0,0,0,0])
        temp = file_[1]
        for fileName in temp:
            # print("Filepath: {}, FileName: {}".format(file_[0], fileName))

            t = read_tensor_from_image_file(
                file_[0] + "/" + fileName,
                input_height=input_height,
                input_width=input_width,
                input_mean=input_mean,
                input_std=input_std)


            with tf.Session(graph=graph) as sess:
                results = sess.run(output_operation.outputs[0], {
                    input_operation.outputs[0]: t
                })
            results = np.squeeze(results)

            #top_k = results.argsort()[-5:][::-1]
            #print(top_k)
            # temp2 = result[atDis]
            #numberOfPredictedDiseases[top_k[0]] += 1
            # y.append(1)
            # THis is for training set 2
            #malignatScore  = results[0] + results[5] + results[10] + results[11] + results[12]
            # Training set 1
            malignatScore = results[8] + results[9] + results[4] + results[12]
            benignScore = results[0] + results[2] + results[3] + results[6] + results[10] + results[15]
            nonNeoplasticScore = 1 - malignatScore - benignScore
            print("FileName: {}, malignantScore: {}, benignScore: {}, non-neoplasticScore: {}".format(file_[0].split('/')[6], malignatScore, benignScore, nonNeoplasticScore))
            print("LesClass: {}".format(getLesClass(file_[0].split('/')[6])))
            print("PropForClass: {}".format(getProbScoreForClass(getLesClass(file_[0].split('/')[6]), benignScore, nonNeoplasticScore, malignatScore)))
            if(getProbScoreForClass(getLesClass(file_[0].split('/')[6]), benignScore, nonNeoplasticScore, malignatScore) == getMaxProb(benignScore, nonNeoplasticScore, malignatScore)):
                print("Is top prob")
                y.append(1)
            else:
                y.append(0)
    return(sum(y)/len(y))



if __name__ == "__main__":
    file_name = "tensorflow/examples/label_image/data/grace_hopper.jpg"
    model_file = \
    "tensorflow/examples/label_image/data/inception_v3_2016_08_28_frozen.pb"
    label_file = "tensorflow/examples/label_image/data/imagenet_slim_labels.txt"
    input_height = 299
    input_width = 299
    input_mean = 0
    input_std = 255
    input_layer = "input"
    output_layer = "InceptionV3/Predictions/Reshape_1"

    parser = argparse.ArgumentParser()
    parser.add_argument("--test_path", help="Test set path")
    parser.add_argument("--image", help="image to be processed")
    parser.add_argument("--graph", help="graph/model to be executed")
    parser.add_argument("--labels", help="name of file containing labels")
    parser.add_argument("--input_height", type=int, help="input height")
    parser.add_argument("--input_width", type=int, help="input width")
    parser.add_argument("--input_mean", type=int, help="input mean")
    parser.add_argument("--input_std", type=int, help="input std")
    parser.add_argument("--input_layer", help="name of input layer")
    parser.add_argument("--output_layer", help="name of output layer")
    args = parser.parse_args()

    if args.test_path:
        test_path = args.test_path
    if args.graph:
        model_file = args.graph
    if args.image:
        file_name = args.image
    if args.labels:
        label_file = args.labels
    if args.input_height:
        input_height = args.input_height
    if args.input_width:
        input_width = args.input_width
    if args.input_mean:
        input_mean = args.input_mean
    if args.input_std:
        input_std = args.input_std
    if args.input_layer:
        input_layer = args.input_layer
    if args.output_layer:
        output_layer = args.output_layer


    graph = load_graph(model_file)
    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    labels = load_labels(label_file)
    y = []
    f = []
    for (dirpath, dirnames, filenames) in walk(test_path):
        f.append([dirpath,filenames])

    for file_ in f:
        # numberOfPredictedDiseases.append([0,0,0,0,0,0,0,0,0])
        temp = file_[1]
        for fileName in temp:

            t = read_tensor_from_image_file(
                file_[0] + "/" + fileName,
                input_height=input_height,
                input_width=input_width,
                input_mean=input_mean,
                input_std=input_std)


            with tf.Session(graph=graph) as sess:
                results = sess.run(output_operation.outputs[0], {
                    input_operation.outputs[0]: t
                })
            results = np.squeeze(results)

            benignScore = 0
            nonNeoplasticScore = 0
            malignantScore = 0
            for lesIndex in range(0,len(labels)):
                class_ = getLesClass(labels[lesIndex])
                if  class_ is "Benign":
                    benignScore += results[lesIndex]
                elif class_ is "nonNeoplastic":
                    nonNeoplasticScore += results[lesIndex]
                elif class_ is "malignant":
                    malignantScore += results[lesIndex]

            print("FileName: {}, malignantScore: {}, benignScore: {}, non-neoplasticScore: {}".format(file_[0].split('/')[6], malignantScore, benignScore, nonNeoplasticScore))
            if getLesClass(file_[0].split('/')[6]) == -1:
                print("LesClass: {}".format(getLesClass(file_[0].split('/')[6])))
            print("PropForClass: {}".format(getProbScoreForClass(getLesClass(file_[0].split('/')[6]), benignScore, nonNeoplasticScore, malignantScore)))
            if(getProbScoreForClass(getLesClass(file_[0].split('/')[6]), benignScore, nonNeoplasticScore, malignantScore) == getMaxProb(benignScore, nonNeoplasticScore, malignantScore)):
                print("Is top prob")
                y.append(1)
            else:
                y.append(0)
    print(sum(y)/len(y))
