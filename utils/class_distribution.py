import pandas as pd
import numpy as np
import glob


def main():
    class_list = pd.read_csv('class_list.txt', header=None)
    class_occurrences = np.zeros((class_list.shape[0], 1), dtype=np.int32)
    label_files = glob.glob('bbox_txt/*.txt')
    for file_path in label_files:
        df = pd.read_csv(file_path, header=None, sep=" ")
        df.iloc[:, 0] = df.iloc[:, 0].astype('int32')
        for index, row in df.iterrows():
            index = int(row.iloc[0])
            class_occurrences[index] += 1
    for i in range(class_occurrences.shape[0]):
        print(f"{class_list.iloc[i, 0]}: {class_occurrences[i, 0]}")


if __name__ == "__main__":
    main()

