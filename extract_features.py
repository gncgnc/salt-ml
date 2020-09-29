import argparse
import sys
import numpy as np
import json
import os
from os.path import isfile, join
import keras
from keras.preprocessing import image
from keras.applications.imagenet_utils import decode_predictions, preprocess_input
from keras.models import Model
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from scipy.spatial import distance

def process_arguments(args):
    parser = argparse.ArgumentParser(description='extract feature vectors')
    parser.add_argument('--input_path', action='store', help='path to input data json')
    parser.add_argument('--output_path', action='store', help='path output json file')
    parser.add_argument('--num_images', action='store', help='max number of images to process', default=20)
    parser.add_argument('--num_components', action='store', help='number of dimensions for PCA', default=10)
    params = vars(parser.parse_args(args))
    return params

def get_image(path, input_shape):
    img = image.load_img(path, target_size=input_shape)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return x

def get_all_image_paths(images_json, num_images):
    '''
    Get image paths from jsonified image data
    '''
    images = []
    with open(images_json) as f:
        data = json.load(f)["data"]
        i = 0
        for image_data in data.values() :
            if i == num_images: break
            i += 1

            images.append(image_data["path"])

    return images

def analyze_images(images_path, num_images, num_components):
    # make feature_extractor
    model = keras.applications.VGG16(weights='imagenet', include_top=True)
    feat_extractor = Model(inputs=model.input, outputs=model.get_layer("fc2").output)
    input_shape = model.input_shape[1:3]

    # get images
    candidate_images = get_all_image_paths(images_path, num_images)

    # analyze images and grab activations
    activations = []
    images = []
    for idx, image_path in enumerate(candidate_images):
        img = get_image(image_path, input_shape)
        if img is not None:
            print("getting activations for %s %d/%d" % (image_path,idx,len(candidate_images)))
            acts = feat_extractor.predict(img)[0]
            activations.append(acts)
            images.append(image_path)
    # run PCA to reduce dimensions
    print("Running PCA on %d images..." % len(activations))
    features = np.array(activations)
    pca = PCA(n_components=num_components)
    pca.fit(features)
    pca_features = pca.transform(features)
    return images, pca_features

def compute_and_save_features(input_path, output_path, num_images, num_components):
    '''
    Save feature vector data. Dimensionality is reduced using PCA. 
    The format of the saved data is:
    {
        <image_id>: { 
            "path": <path to image>
            "features": <feature vector of the image>
        }
        ...
    } 
    '''
    images, pca_features = analyze_images(input_path, num_images, num_components)
    
    X = np.array(pca_features)
    data = dict()
    for i in range(len(images)):
        id = os.path.splitext(os.path.basename(images[i]))[0]
        data[id] = {"path": images[i], "features": [round(x,3) for x in X[i].tolist()]}

    with open(output_path, 'w') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)



if __name__ == '__main__':
    params = process_arguments(sys.argv[1:])
    images_path = params['input_path']
    output_path = params['output_path']
    num_images = params['num_images']
    num_components = params['num_components']

    compute_and_save_features(images_path, output_path, num_images, num_components)
    print("finished saving %s" % output_path)
