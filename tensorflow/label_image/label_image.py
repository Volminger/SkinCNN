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


import matplotlib.pyplot as plt


benignLes = ["seborrheic keratosis", "seborrheic keratosis bucket", "epidermal tumor benign bucket", "nevus", "pigmented lesion benign bucket", "dermal tumor benign", "solar lentigo (PIGMENTED LESION BENIGN-BUCKET)", "Eczema Spongiotic Dermatitis", "PIGMENTED LESION BENIGN-BUCKET", "Seborrheic Keratosis-BUCKET"]
nonNeoplasticLes = ["rosacea rhinophyma and variants", "acne folliculitis hidradenitis and diseases of appendegeal structures bucket", "acne vulgaris", "psoriasis pityriasis rubra pilaris and papulosquamous disorders", "inflammatory bucket", "eczema spongiotic dermatitis", "Acne Folliculitis Hidradenitis And Diseases Of Appendegeal Structures-BUCKET", "INFLAMMATORY-BUCKET"]
maligantLes = ["maligant","MELANOMA", "basal cell carcinoma", "pigmented lesion malignant bucket", "epidermal tumor malignant bucket", "squamous cell carcinoma (EPIDERMAL TUMOR MALIGNANT-BUCKET)", "Eczema Spongiotic Dermatitis", "PIGMENTED LESION MALIGNANT-BUCKET"]
upperCaseBenignLes = [x.upper() for x in benignLes]
upperCaseNonNeoplasticLes = [x.upper() for x in nonNeoplasticLes]
upperCaseMaligantLes = [x.upper() for x in maligantLes]

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
    elif lesName.upper() in upperCaseMaligantLes:
        return "maligant"
    return "Les not found"

def getProbScoreForClass(className, benProp, nonProp, malProp):
    if className is "Benign":
        return benProp
    elif className is "nonNeoplastic":
        return nonProp
    elif className is "maligant":
        return malProp
    return -1

def getMaxProb(benProp, nonProp, malProp):
    listProb = [benProp, nonProp, malProp]
    return max(listProb)

def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph


def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.read_file(file_name, input_name)
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
    parser.add_argument("--test_disease", help="The disease of the images in the test folder")
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
    if args.test_disease:
        test_disease = args.test_disease
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
    # numberOfPredictedDiseases = [0,0,0,0,0,0,0,0,0]
    #indexForDiseaseToBeTested = labels.index(test_disease)
    result = []
    y = []
    yscore = []
    atDis = -1

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

            top_k = results.argsort()[-5:][::-1]
            # temp2 = result[atDis]
            # numberOfPredictedDiseases[top_k[0]] += 1
            # y.append(1)

            benignScore = 0
            nonNeoplasticScore = 0
            malignatScore = 0
            for lesIndex in range(0,len(labels)):
                class_ = getLesClass(labels[lesIndex])
                if  class_ is "Benign":
                    benignScore += results[lesIndex]
                elif class_ is "nonNeoplastic":
                    nonNeoplasticScore += results[lesIndex]
                elif class_ is "maligant":
                    malignatScore += results[lesIndex]
            print(file_[0])
            if test_disease in file_[0]:
                print("Inside if")
                y.append(1)
            else:
                y.append(0)
            if getLesClass(test_disease) is "maligant":
                yscore.append(malignatScore)
            elif getLesClass(test_disease) is "Benign":
                yscore.append(1 - malignatScore)
            else:
                yscore.append(1 - malignatScore)
            print("FileName: {}, maligantScore: {}, benignScore: {}, non-neoplasticScore: {}".format(file_[0].split('/')[6], malignatScore, benignScore, nonNeoplasticScore))
            #result.append([labels[top_k[0]],results[indexForDiseaseToBeTested]])
            # print("Top: {}".format(labels[top_k[0]]))
        # atDis += 1
    # print("\n Testing {}".format(test_disease))
    # print("NumberOfPredictedDiseases")
    # for i, label in enumerate(labels):
    #     print("    {}: {}".format(label, numberOfPredictedDiseases[i]))
    # print("\n")
    # for i in result:
    #     print("Predicted disease: {},".format(i[0]))
    #     print("  {} probability: {}".format(test_disease, i[1]))
    print(y)
    print(yscore)

    # Compute ROC curve and ROC area for each class
    # fpr = dict()
    # tpr = dict()
    # roc_auc = dict()
    # #for i in range(labels):
    #    fpr[i], tpr[i], _ = roc_curve(y[:, i], y_score[:, i])
    #    roc_auc[i] = auc(fpr[i], tpr[i])
    fpr, tpr, _ = roc_curve(y, yscore, 1)
    roc_auc = auc(fpr, tpr)
    print(fpr)
    print(tpr)

    plt.figure()
    lw = 2
    plt.plot(fpr, tpr, color='darkorange',
             lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()

  # graph = load_graph(model_file)
  # t = read_tensor_from_image_file(
  #     file_name,
  #     input_height=input_height,
  #     input_width=input_width,
  #     input_mean=input_mean,
  #     input_std=input_std)
  #
  # input_name = "import/" + input_layer
  # output_name = "import/" + output_layer
  # input_operation = graph.get_operation_by_name(input_name)
  # output_operation = graph.get_operation_by_name(output_name)
  #
  # with tf.Session(graph=graph) as sess:
  #   results = sess.run(output_operation.outputs[0], {
  #       input_operation.outputs[0]: t
  #   })
  # results = np.squeeze(results)
  #
  # top_k = results.argsort()[-5:][::-1]
  # labels = load_labels(label_file)
  # for i in top_k:
  #   print(labels[i], results[i])
