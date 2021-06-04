import os
from sklearn.model_selection import train_test_split


def image_file_names(directory_path="/media/robert/1TB HDD/scene_crops/grouped_scene/training"):

    X, y = [], []
    all_files = os.listdir(directory_path)
    all_files.sort() # ensure correct ordering
    for file in os.listdir(directory_path):
        if file.endswith(".jpg"):
            X.append(file)
        elif file.endswith(".txt"):
            y.append(file)

    return X, y


def image_train_test_txt(X_train, X_test):
    path = "/home/people/06681344/scratch/data/"

    with open("train.txt", "w") as output_train:
        for file_name in X_train:
            output_train.write(path + file_name)
            output_train.write("\n")

    with open("test.txt", "w") as output_test:
        for file_name in X_test:
            output_test.write(path + file_name)
            output_test.write("\n")

