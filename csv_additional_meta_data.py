
# add image dimensions to metadata csv - new columns [image_width] [image_height]
def image_dimensions(df):
    pano_ids = set(df['gsv_panorama_id'])
    counter = 1
    for pano_id in pano_ids:
        counter += 1
        if counter % 5000 == 0:
            print("On iteration {}/{}".format(counter, len(pano_ids)))

        image_path_folder = image_path + pano_id[:2] + "/"
        image_name = image_path_folder + pano_id + ".jpg"

        if os.path.exists(image_name):
            try:
                im = Image.open(image_name)
                im_width = im.size[0]
                im_height = im.size[1]
                df.loc[df['gsv_panorama_id'] == pano_id, ['image_width', 'image_height']] = im_width, im_height
            except:
                print(sys.exc_info()[0])
                print("Pano-id causing error", pano_id)
        else:
            continue
    return df


# add additional metadata to csv
def additional_meta(df):
    df['scaling_factor'] = df['image_width'] / 13312
    df['x'] = (((180 - (df['photographer_heading'])) / 360) * df['image_width'] + (
                df['scaling_factor'] * df['sv_image_x'])) % df['image_width']
    df['y'] = df['image_height'] / 2 - (df['scaling_factor'] * df['sv_image_y'])
    df['distance'] = 19.80546390 + 0.01523952 * (df['sv_image_y'])
    df['crop_size'] = 0
    df.loc[df['distance'] < 0, 'distance'] = 0
    df.loc[df['distance'] > 0, 'crop_size'] = 8725.6 * (df['distance'] ** -1.192)
    df.loc[(df['crop_size'] > 1500) | (df['crop_size'] == 0), 'crop_size'] = 1500
    df.loc[df['crop_size'] < 50] = 50
    df = df.sort_values(by=['x', 'y'])

    return df