
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