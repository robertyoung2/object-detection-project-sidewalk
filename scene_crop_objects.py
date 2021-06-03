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