import os
import numpy as np
import sys

def main():
    dir_path = sys.argv[1]
    find_empty_npy_files(dir_path)


def find_empty_npy_files(directory):
    # Make sure the directory exists
    if not os.path.isdir(directory):
        print(f"The directory {directory} does not exist.")
        return

    # Loop over all the files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.npy'):
            file_path = os.path.join(directory, filename)
            try:
                # Load the numpy array
                data = np.load(file_path)
                #print(file_path)
                # If the array is empty, print its name
                if np.isnan(data).any():
                    print(f"Empty file found(contian nah): {filename}")
                    # os.remove(file_path)
            except Exception as e:
                print(f"Error reading file {filename}: {e}")

if __name__ == "__main__":
    main()