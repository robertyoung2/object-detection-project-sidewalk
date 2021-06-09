import multiprocessing
from multiprocessing import Process

import os
import time
import warnings
import random

import pandas as pd
from PIL import Image, ImageDraw

warnings.filterwarnings('ignore')

image_path = "/media/robert/1TB HDD/testing/"
output_path = "/home/robert/Documents/testing/"

df = pd.read_csv("data_csv/csv-all-metadata-seattle.csv").sort_values(by=['gsv_panorama_id'])
df = df.loc[df['label_type_id'] == 1]  # only look at labels for dropped curbs


def process_panos(pano_ids):
    folder = "overcheck"
    count = 0
    for pano_id in pano_ids:

        df_test_id = df[df['gsv_panorama_id'] == pano_id].copy()
        columns = df_test_id.columns
        counter = 0
        image_path_folder = image_path + pano_id[:2] + "/"
        image_name = image_path_folder + pano_id + ".jpg"

        if not os.path.exists(image_name):
            continue
        count += 1

        while df_test_id.empty is False:
            df_objects = pd.DataFrame(columns=columns)
            compare = df_test_id.iloc[0]
            crop_size, start_distance = predict_crop_size(compare['sv_image_y'])
            df_objects = df_objects.append(compare)
            df_test_id = df_test_id.drop(df_test_id.index[0])
            for index, row in df_test_id.iterrows():
                # the check is 4*crop size as for a total width of 5 crops, 4 is the distance centre point to centre point of crop
                if abs(compare['x'] - row['x']) <= crop_size * 4 and abs(row['distance'] - start_distance) < 3:
                    df_objects = df_objects.append(row)
                    df_test_id = df_test_id.drop(index=row.name)
                elif abs(compare['x'] - row['x']) > crop_size * 4:
                    break
                elif len(df_objects) == 1:
                    break
                else:
                    continue

            counter += 1
            grouped_scene(df_objects, image_name, folder, (pano_id + "_" + str(counter)))
    return count


def valid_labels(pano_ids):

    all_pano_ids = pano_ids
    # random.shuffle(list(all_pano_ids))  # Randomly shuffle the list
    all_pano_ids = list(all_pano_ids)
    valid_ids = []
    for pano_id in all_pano_ids:
        image_path_folder = image_path + pano_id[:2] + "/"
        image_name = image_path_folder + pano_id + ".jpg"
        if os.path.exists(image_name):
            valid_ids.append(pano_id)
    return valid_ids


def predict_crop_size(sv_image_y):
    crop_size = 0
    distance = max(0, 19.80546390 + 0.01523952 * sv_image_y)

    if distance > 0:
        crop_size = 8725.6 * (distance ** -1.192)
    if crop_size > 1500 or distance == 0:
        crop_size = 1500
    if crop_size < 50:
        crop_size = 50
    return crop_size, distance


def grouped_scene(df_input, path_to_image, folder, file_name):
    im = Image.open(path_to_image)
    draw = ImageDraw.Draw(im)

    im_width = im.size[0]
    im_height = im.size[1]

    draw = ImageDraw.Draw(im)
    predicted_crop_size = df_input.iloc[0]['crop_size']

    crop_width = predicted_crop_size
    crop_height = predicted_crop_size

    x = df_input.iloc[[0, -1]]['x'].mean()
    y = df_input.iloc[[0, -1]]['y'].mean()

    top_left_x = x - crop_width / 2
    top_left_y = y - crop_height / 2

    r = 10
    scene_width = [7, 6, 5]
    scene_height = [3.93, 3.43, 2.82]

    top_left_x -= crop_width * ((scene_width[2] - 1) / 2)
    top_left_y -= crop_width * ((scene_height[2] - 1) / 2)

    top_left_x, top_left_y = valid_boundaries(top_left_x, top_left_y, crop_width, crop_height, im_width, im_height,
                                              scene_width, scene_height)

    cropped_square = im.crop(
        (top_left_x, top_left_y, top_left_x + crop_width * scene_width[2], top_left_y + crop_height * scene_height[2]))

    max_size = (2272, 1278)
    file_name = str(file_name)

    cropped_square = cropped_square.resize(max_size, Image.ANTIALIAS)
    draw_2 = ImageDraw.Draw(cropped_square)

    if not os.path.exists(output_path + "grouped_scene/" + folder):
        os.makedirs(output_path + "grouped_scene/" + folder)

    with open(output_path + "grouped_scene/" + folder + "/" + file_name + ".txt", "a") as myfile:

        for index, row in df_input.iterrows():
            bounding_scaled = scale_bounding_box(max_size, scene_width, scene_height, row['x'], row['y'], top_left_x,
                                                 top_left_y, df_input.iloc[0]['crop_size'], row['crop_size'])
            label_2_x, label_2_y, top_left_x_scaled, top_left_y_scaled, crop_width_scaled, crop_height_scaled = bounding_scaled

            # for debug - show centre and bounding box
            draw_2.ellipse((label_2_x - r, label_2_y - r, label_2_x + r, label_2_y + r), fill=128)
            draw_2.rectangle([top_left_x_scaled, top_left_y_scaled, top_left_x_scaled + crop_width_scaled,
                              top_left_y_scaled + crop_height_scaled], outline='red', width=10)

            an = generate_annotations(max_size, label_2_x, label_2_y, crop_width_scaled, crop_height_scaled)

            to_write = (str(row['label_type_id'] - 1), format(an[0], '.6f'), format(an[1], '.6f'), format(an[2], '.6f'),
                        format(an[3], '.6f'))
            to_write = ' '.join(to_write)
            myfile.write(to_write + "\n")

    cropped_square.save(output_path + "grouped_scene/" + folder + "/" + file_name + ".jpg")


def valid_boundaries(top_left_x, top_left_y, crop_width, crop_height, im_width, im_height, scene_width, scene_height):
    # If top_left_x or top_left_y are less than 0 (origin), set to zero
    if top_left_x < 0:
        top_left_x = 0

    if top_left_y < 0:
        top_left_y = 0

    # If X-right or Y-bottom are greater then the image extents, adjust the scene crop
    if top_left_x + crop_width * scene_width[2] > im_width:
        top_left_x -= top_left_x + crop_width * scene_width[2] - im_width

    if top_left_y + crop_height * scene_height[2] > im_height:
        top_left_y -= top_left_y + crop_height * scene_height[2] - im_height

    return top_left_x, top_left_y


def scale_bounding_box(max_size, scene_width, scene_height, x, y, top_left_x, top_left_y, crop_size_base,
                       crop_size_compare):
    crop_width, crop_height = crop_size_base, crop_size_base

    scaling_x = max_size[0] / (crop_width * scene_width[2])
    scaling_y = max_size[1] / (crop_height * scene_height[2])

    label_2_x = scaling_x * (x - top_left_x)
    label_2_y = scaling_y * (y - top_left_y)

    crop_width_scaled = scaling_x * crop_size_compare
    crop_height_scaled = scaling_y * crop_size_compare

    top_left_x_scaled = label_2_x - crop_width_scaled / 2
    top_left_y_scaled = label_2_y - crop_height_scaled / 2

    return label_2_x, label_2_y, top_left_x_scaled, top_left_y_scaled, crop_width_scaled, crop_height_scaled


def generate_annotations(dimensions, label_2_x, label_2_y, crop_width_scaled, crop_height_scaled):
    x_normalised, width_normalised = round(label_2_x / dimensions[0], 6), round(crop_width_scaled / dimensions[0], 6)
    y_normalised, height_normalised = round(label_2_y / dimensions[1], 6), round(crop_height_scaled / dimensions[1], 6)

    return x_normalised, y_normalised, width_normalised, height_normalised


def main():
    print("Starting group scene processing.")
    df = pd.read_csv("data_csv/csv-all-metadata-seattle.csv").sort_values(by=['gsv_panorama_id'])
    df = df.loc[df['label_type_id'] == 1]  # only look at labels for dropped curbs
    start_time = time.time()
    # total_processed = process_panos(set(df['gsv_panorama_id']))
    pano_ids = set(df['gsv_panorama_id'])
    valid_ids = valid_labels(pano_ids)
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(process_panos, (pano_ids,))

    end_time = time.time() - start_time
    if end_time < 60:
        minutes = 0
        seconds = round(end_time % 60, 0)
    else:
        minutes = round(end_time / 60, 0)
        seconds = round(end_time % 60, 0)
    print("Time taken {} minutes and {} seconds.".format(minutes, seconds))


if __name__ == "__main__":
    main()

