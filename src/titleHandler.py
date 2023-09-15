
import os

class TitleHandler:
    def __init__(self, INDEX_FOLDER_PATH, TITLE_FILE_CAP):
        self.INDEX_FOLDER_PATH = INDEX_FOLDER_PATH
        self.TITLE_FILE_CAP = TITLE_FILE_CAP
        self.title_file_count = 0
        self.titles = []

    def _dump_titles_to_file(self):
        title_file_name = "title_" + str(self.title_file_count) + ".txt"
        with open(os.path.join(self.INDEX_FOLDER_PATH, title_file_name), "w", encoding='utf-8') as title_fp:
            for title in self.titles:
                title_fp.write(title + "\n")
        
        self.title_file_count += 1
        self.titles = []
        
    def add_title(self, title, isLast = False):
        if(isLast == False):
            self.titles.append(title)
        if(isLast == True or len(self.titles) == self.TITLE_FILE_CAP) :
            self._dump_titles_to_file()
        