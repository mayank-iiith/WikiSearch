
import os

class TitleHandler:
    def __init__(self, INDEX_FOLDER_PATH, TITLE_FILE_CAP):
        # Initialize the TitleHandler with the folder path and title file capacity.
        self.INDEX_FOLDER_PATH = INDEX_FOLDER_PATH
        self.TITLE_FILE_CAP = TITLE_FILE_CAP
        self.title_file_count = 0
        self.titles = []

    def _dump_titles_to_file(self):
        # Write the accumulated titles to a title file.

        title_file_name = "title_" + str(self.title_file_count) + ".txt"
        with open(os.path.join(self.INDEX_FOLDER_PATH, title_file_name), "w", encoding='utf-8') as title_fp:
            for title in self.titles:
                title_fp.write(title + "\n")
        
        # Increment the title file count and reset the titles list.
        self.title_file_count += 1
        self.titles = []
        
    def add_title(self, title, isLast = False):
        # Add a title to the list of titles.

        if(isLast == False):
            self.titles.append(title)

        # Dump titles to a file when the specified cap is reached or it's the last title.
        if(isLast == True or len(self.titles) == self.TITLE_FILE_CAP) :
            self._dump_titles_to_file()

    def get_title(self, docID):
        # Retrieve the title for a given document ID.

        docID = int(docID)
        title_idx = docID // self.TITLE_FILE_CAP
        title_offset = docID % self.TITLE_FILE_CAP
        title_file_name = "title_" + str(title_idx) + ".txt"
        
        # Open the appropriate title file and read the title.
        with open(os.path.join(self.INDEX_FOLDER_PATH, title_file_name), "r", encoding='utf-8') as title_fp:
            lines = title_fp.readlines()
        
        title = lines[title_offset].strip("\n")
        return title
        