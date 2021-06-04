import os
from sklearn.model_selection import train_test_split


def image_file_names(directory_path="/media/robert/1TB HDD/scene_crops/grouped_scene/all_data"):

    x, y = [], []
    all_files = os.listdir(directory_path)
    all_files.sort()  # ensure correct ordering
    for file in os.listdir(directory_path):
        if file.endswith(".jpg"):
            x.append(file)
        elif file.endswith(".txt"):
            y.append(file)
    return x, y


def image_train_test_txt(x_train, x_test):

    path = "/home/people/06681344/scratch/data/"

    with open("train.txt", "w") as output_train:
        for file_name in x_train:
            output_train.write(path + file_name)
            output_train.write("\n")

    with open("test.txt", "w") as output_test:
        for file_name in x_test:
            output_test.write(path + file_name)
            output_test.write("\n")


def split_data(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
    return x_train, x_test, y_train, y_test


def main():
    x, y = image_file_names()
    print(len(x), len(y))
    x_train, x_test, y_train, y_test = split_data(x, y)
    image_train_test_txt(x_train, x_test)


if __name__ == "__main__":
    main()