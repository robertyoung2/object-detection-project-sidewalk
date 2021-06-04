import os


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

