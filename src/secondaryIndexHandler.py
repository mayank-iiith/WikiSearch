import os

class SecondaryIndexHandler:
    def __init__(self, INDEX_FOLDER_PATH):
        # Initialize the SecondaryIndexHandler with the folder path.
        self.INDEX_FOLDER_PATH = INDEX_FOLDER_PATH
        self.SecondaryIndexFileCount = 1
        self.secondary_index_file_name = "secondary_index.txt"
        self.secondary_index_word = []

    def build_secondary_index(self):
        # Build the secondary index from the primary index files.

        print("Secondary Index Creation Started")

        # Iterate through files in the index folder.
        for file in os.listdir(self.INDEX_FOLDER_PATH):
            if(file.startswith("index_")):
                with open(os.path.join(self.INDEX_FOLDER_PATH, file), "r", encoding='utf-8') as fp:
                    # Read the first line of each primary index file and extract the word.
                    line = fp.readline().strip("\n").split("=")
                    self.secondary_index_word.append(line[0])
        
        # Sort the list of words since files are picked up in a random order.
        self.secondary_index_word.sort()

        # Write the sorted words to the secondary index file.
        with open(os.path.join(self.INDEX_FOLDER_PATH, self.secondary_index_file_name), "w", encoding='utf-8') as secondary_fp:
            for word in self.secondary_index_word:
                secondary_fp.write(word + "\n")

        print("Secondary Index Creation Completed")


    def load_secondary_index(self):
        # Load the secondary index from the secondary index file.

        with open(os.path.join(self.INDEX_FOLDER_PATH, self.secondary_index_file_name), "r", encoding='utf-8') as secondary_fp:
            lines = secondary_fp.readlines()
            for line in lines:
                word = line.strip("\n")
                self.secondary_index_word.append(word)

        print("Secondary Index Got Loaded")


    def get_index_file_idx(self, word):
        # Get the index of the primary index file for a given word.

        for idx, entry in enumerate(self.secondary_index_word):
            if(word < entry):
                # Return the previous index since the list is sorted.
                return idx - 1
        # Return the last index if the word is greater than all entries.
        return len(self.secondary_index_word) - 1 


