import xml.sax
import os

from preprocessor import Preprocessor
from titleHandler import TitleHandler
from invertedIndexHandler import InvertedIndexHandler

class WikiHandler(xml.sax.ContentHandler):
    def __init__(self, INDEX_FOLDER_PATH, MAX_WORD_CAP, TITLE_FILE_CAP, INVERTED_INDEX_TEMP_FILE_CAP, FINAL_INDEX_FILE_CAP):
        # Initialize the WikiHandler with various parameters and objects.

        self.INDEX_FOLDER_PATH = INDEX_FOLDER_PATH
        self.MAX_WORD_CAP = MAX_WORD_CAP
        self.TITLE_FILE_CAP = TITLE_FILE_CAP
        self.INVERTED_INDEX_TEMP_FILE_CAP = INVERTED_INDEX_TEMP_FILE_CAP
        self.FINAL_INDEX_FILE_CAP = FINAL_INDEX_FILE_CAP

        # Initialize counters for statistics
        self.TotalDocCount = 0
        self.TotalWordsEncountered = 0
        self.TotalUniqueWords = 0
        self.TotalWords = 0
        self.TitleFileCount = 0
        self.PrimaryIndexFileCount = 0

        # Define allowed XML tags and fields.
        self.allowed_tags = ["title", "text"]
        self.fields = ["title", "body", "infobox", "category", "link", "reference"]
        self.docID = 0
        self.current_tag = ""
        self.page_data = {}
        self.wiki_data = {}

        # Create instances of preprocessor, title handler, and inverted index handler.
        self.preprocessor = Preprocessor(self.MAX_WORD_CAP)
        self.titleHandler = TitleHandler(self.INDEX_FOLDER_PATH, self.TITLE_FILE_CAP)
        self.invertedIndexHandler = InvertedIndexHandler(self.INDEX_FOLDER_PATH, self.INVERTED_INDEX_TEMP_FILE_CAP, self.FINAL_INDEX_FILE_CAP)

    def startElement(self, tag, attributes):
        # Handle the start of an XML element.

        self.current_tag = tag
        if(tag == 'page'):
            self.page_data = {}
            for tag in self.allowed_tags:
                self.page_data[tag] = ""

            self.wiki_data = {}
            for field in self.fields:
                self.wiki_data[field] = ""

    def endElement(self, tag):
        # Handle the end of an XML element.

        if(tag == 'page'):
            if len(self.page_data["title"]) > 0 and len(self.page_data["text"]) > 0:
                # Process title and text data.
                self.wiki_data['title'] = self.preprocessor.process_title(self.page_data['title'])
                self.wiki_data['infobox'], self.wiki_data['body'], self.wiki_data['category'], self.wiki_data['link'], self.wiki_data['reference'] = self.preprocessor.process_text(self.page_data['text'])
                
                # Add title and inverted index data.
                self.titleHandler.add_title(self.page_data["title"].replace("\n", " "))
                self.invertedIndexHandler.add_inverted_index(self.docID, self.wiki_data)

                if(self.docID % 1000 == 0):
                    print("Document Processed :", self.docID, end = "\r")
                self.docID += 1


        # Handle the end of the "mediawiki" element to finalize processing.
        if tag == "mediawiki":
            print("Document Processed :", self.docID)

            # Add the last chunk of title and inverted index data.
            self.titleHandler.add_title(title = None, isLast = True)
            self.invertedIndexHandler.add_inverted_index(docID = None, wiki_data = None, isLast = True)
            self.invertedIndexHandler.merge_temp_indexes()

            # Update counters and statistics.
            self.TotalDocCount = self.docID
            self.TotalWordsEncountered = self.preprocessor.TotalWordsEncountered
            self.TotalUniqueWords = self.invertedIndexHandler.total_unique_words
            self.TotalWords = self.invertedIndexHandler.total_words
            self.TitleFileCount = self.invertedIndexHandler.temp_index_file_count
            self.PrimaryIndexFileCount = self.invertedIndexHandler.final_index_file_count

    def characters(self, content):
        # Handle character content within XML elements.

        if self.current_tag in self.allowed_tags:
            self.page_data[self.current_tag] += content.strip()
