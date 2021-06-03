import pandas as pd
import numpy as np
from PIL import Image
from PIL import Image, ImageDraw
import os, sys, random
import warnings
warnings.filterwarnings('ignore')


def process_panos(df, pano_ids):
    folder = "overcheck"
    count = 0
    for pano_id in pano_ids:
        if count == 1000:
            break

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
