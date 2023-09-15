import os

class SecondaryIndexHandler:
    def __init__(self, INDEX_FOLDER_PATH):
        self.INDEX_FOLDER_PATH = INDEX_FOLDER_PATH
        self.SecondaryIndexFileCount = 1

    def build_secondary_index(self):
        print("Secondary Index Creation Started")
        first_word_file = []
        for file in os.listdir(self.INDEX_FOLDER_PATH):
            if(file.startswith("index_")):
                with open(os.path.join(self.INDEX_FOLDER_PATH, file), "r", encoding='utf-8') as fp:
                    line = fp.readline().strip("\n").split("=")
                    first_word_file.append(line[0])
        
        # because files are picked up in a random order, sort the list
        first_word_file.sort()

        secondary_file_name = "secondary_index.txt"
        with open(os.path.join(self.INDEX_FOLDER_PATH, secondary_file_name), "w", encoding='utf-8') as secondary_fp:
            for word in first_word_file:
                secondary_fp.write(word + "\n")
        print("Secondary Index Creation Completed")
