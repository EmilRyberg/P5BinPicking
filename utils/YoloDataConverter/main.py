import pandas as pd
import numpy as np
import math
import glob


def main():
    data_files = glob.glob("data/*.txt")
    print("Indexing classes...")
    counter = 1
    class_count = 0
    max_class_number = -1
    data_frames_with_file_path = []

    for file_name in data_files:
        df = pd.read_csv(file_name, sep=" ", names=["class", "x", "y", "width", "height"])
        data_frames_with_file_path.append((df, file_name))
        if counter < len(data_files):
            print("Processing file {0}/{1}".format(counter, len(data_files)), end="\r", flush=True)
        else:
            print("Processing file {0}/{1}".format(counter, len(data_files)))

        for c in df['class']:
            if c > max_class_number:
                max_class_number = c

        counter += 1

    class_count = max_class_number + 1
    print("Found {0} classes in total".format(class_count))

    valid_result = False
    while not valid_result:
        grid_size = input("Specify grid size (assuming nxn grid): ")
        try:
            grid_size = int(grid_size)
            valid_result = True
        except ValueError:
            continue
    print("Grid size will be {0}x{0}".format(grid_size))

    for (df, file_name) in data_frames_with_file_path:
        create_tensor_for_image(grid_size, class_count, df, file_name.replace('.txt', '-full-data.npy'))


def create_tensor_for_image(grid_size, num_classes, data_frame, save_path, num_anchor_boxes=1):
    feature_vector_size = num_classes + 5  # 5 for object in box flag, x, y, width and height
    tensor = np.zeros((grid_size, grid_size, num_anchor_boxes, feature_vector_size))
    grid_cell_map = np.zeros((grid_size, grid_size))
    for index, data in data_frame.iterrows():
        class_oh_encoded = np.zeros((num_classes, 1))
        class_oh_encoded[int(data["class"])] = 1
        rest_of_features = data.iloc[1:].to_numpy()
        rest_of_features = np.reshape(rest_of_features, (rest_of_features.shape[0], 1))
        feature_vector = np.append(class_oh_encoded, rest_of_features, axis=0)
        feature_vector = np.append(np.array([[1]]), feature_vector, axis=0)
        feature_vector = np.reshape(feature_vector, (feature_vector.shape[0],))
        grid_row, grid_col = get_grid_cell(data["x"], data["y"], grid_size)
        if grid_cell_map[grid_row, grid_col] != 1:
            grid_cell_map[grid_row, grid_col] = 1
            tensor[grid_row, grid_col, 0] = feature_vector
        else:
            print("WARNING: Grid cell {0}, {1} is already occupied.".format(grid_row, grid_col))
    print("Saving file as {0}".format(save_path.split("\\", 1)[1]))
    np.save(save_path, tensor)


def get_grid_cell(x, y, grid_size):
    return math.floor(y * (grid_size-1)), math.floor(x * (grid_size-1))


if __name__ == '__main__':
    main()
