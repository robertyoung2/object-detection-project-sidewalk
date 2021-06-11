import pickle


def directory_mapper(file_path):
    with open(file_path) as f:
        lines = f.readlines()

    directories = []
    for line in lines:
        line = line[2:-1]
        directories.append(line)

    print("There are a total of:", len(directories), "directories.")

    directories_dict = {}
    for direct in directories:
        lowered = direct.lower()
        directories_dict[lowered] = direct
    print(directories_dict)

    with open('data_text/directories.pickle', 'wb') as handle:
        pickle.dump(directories_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


def main():
    file_path = 'data_text/directories.txt'
    directory_mapper(file_path)


if __name__ == "__main__":
    main()
