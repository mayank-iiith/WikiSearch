import os
import math
import heapq
from collections import defaultdict

class InvertedIndexHandler:
    def __init__(self, INDEX_FOLDER_PATH, INVERTED_INDEX_TEMP_FILE_CAP, FINAL_INDEX_FILE_CAP):
        # Initialize the InvertedIndexHandler with folder paths and caps.
        self.INDEX_FOLDER_PATH = INDEX_FOLDER_PATH
        self.INVERTED_INDEX_TEMP_FILE_CAP = INVERTED_INDEX_TEMP_FILE_CAP
        self.FINAL_INDEX_FILE_CAP = FINAL_INDEX_FILE_CAP
        
        # Initialize data structures for temporary and final inverted indexes.
        self.inverted_index = {}
        self.inverted_index_size = 0
        self.temp_index_file_count = 0
        
        self.final_inverted_index = {}
        self.final_inverted_index_size = 0
        self.final_index_file_count = 0

        # Initialize counters for document statistics.
        self.total_doc_count = 0
        self.total_unique_words = 0
        self.total_words = 0

    def _dump_inverted_index_to_temp_index_file(self):
        # Write the current temporary inverted index to a file.
        temp_index_file_name = "temp_index_" + str(self.temp_index_file_count) + ".txt"
        with open(os.path.join(self.INDEX_FOLDER_PATH, temp_index_file_name), "w", encoding='utf-8') as temp_index_fp:
            for word in sorted(self.inverted_index):
                doc_count = self.inverted_index[word]["doc_count"]
                total_count = self.inverted_index[word]["total_count"]
                posting_list = '|'.join(self.inverted_index[word]["posting_list"])
                temp_index_fp.write(word + "=" + str(doc_count) + "=" + str(total_count) + "=" + posting_list + "\n")
        
        # Reset the temporary inverted index.
        self.temp_index_file_count += 1
        self.inverted_index = {}
        self.inverted_index_size = 0
    
    def add_inverted_index(self, docID, wiki_data, isLast = False):
        # Add document data to the inverted index.

        if(isLast == False):
            # Update document count for statistics.
            self.total_doc_count = docID + 1

            # Separate document data into different sections.
            title = wiki_data['title']
            infobox = wiki_data['infobox']
            body = wiki_data['body']
            category = wiki_data['category']
            link = wiki_data['link']
            reference = wiki_data['reference']

            # Initialize dictionaries to count word occurrences.
            combined_dict = defaultdict(int)
            title_dict = defaultdict(int)
            infobox_dict = defaultdict(int)
            body_dict = defaultdict(int)
            category_dict = defaultdict(int)
            link_dict = defaultdict(int)
            reference_dict = defaultdict(int)

            # Count word occurrences in each section.
            for word in title:
                title_dict[word] += 1
                combined_dict[word] += 1

            for word in infobox:
                infobox_dict[word] += 1
                combined_dict[word] += 1

            for word in body:
                body_dict[word] += 1
                combined_dict[word] += 1

            for word in category:
                category_dict[word] += 1
                combined_dict[word] += 1

            for word in link:
                link_dict[word] += 1
                combined_dict[word] += 1

            for word in reference:
                reference_dict[word] += 1
                combined_dict[word] += 1

            # Create an index string for each word and update the inverted index.
            for word, word_count_in_doc in combined_dict.items():
                index_string = str(docID) + " "
                if(title_dict[word] > 0):
                    index_string += "t" + str(title_dict[word]) + "-"
                if(infobox_dict[word] > 0):
                    index_string += "i" + str(infobox_dict[word]) + "-"
                if(body_dict[word] > 0):
                    index_string += "b" + str(body_dict[word]) + "-"
                if(category_dict[word] > 0):
                    index_string += "c" + str(category_dict[word]) + "-"
                if(link_dict[word] > 0):
                    index_string += "l" + str(link_dict[word]) + "-"
                if(reference_dict[word] > 0):
                    index_string += "r" + str(reference_dict[word]) + "-"
                index_string = index_string[:-1]

                if word not in self.inverted_index:
                    self.inverted_index[word] = {"doc_count":0, "total_count": 0, "posting_list": []}
                self.inverted_index[word]["doc_count"] += 1
                self.inverted_index[word]["total_count"] += word_count_in_doc
                self.inverted_index[word]["posting_list"].append(index_string)
                self.inverted_index_size += len(index_string)

        if(isLast == True or self.inverted_index_size >= self.INVERTED_INDEX_TEMP_FILE_CAP):
            # If the temporary index is full or it's the last document, dump it to a file.
            self._dump_inverted_index_to_temp_index_file()


    def _dump_final_inverted_index_to_file(self):
        # Write the final inverted index to a file.
        final_index_file_name = "index_" + str(self.final_index_file_count) + ".txt"
        with open(os.path.join(self.INDEX_FOLDER_PATH, final_index_file_name), "w", encoding='utf-8') as final_index_fp:
            for word in sorted(self.final_inverted_index):
                final_index_fp.write(self.final_inverted_index[word] + "\n")
        
        # Reset the final inverted index.
        self.final_index_file_count += 1
        self.final_inverted_index = {}
        self.final_inverted_index_size = 0

    def _get_IDF(self, doc_count):
        # Calculate and return the Inverse Document Frequency (IDF) for a word.
        return math.log10(self.total_doc_count / doc_count)

    def _add_final_inverted_index(self, word, doc_count, word_freq, posting_list, isLast = False):
        # Add word and its associated data to the final inverted index.

        if(isLast == False):
            idf = self._get_IDF(doc_count)
            self.final_inverted_index[word] = word + "=" + str(idf) + "=" + str(doc_count) + "=" + str(word_freq) + "=" + posting_list
            self.final_inverted_index_size += len(self.final_inverted_index[word])
            self.total_unique_words += 1
            self.total_words += word_freq

        if(isLast == True or self.final_inverted_index_size >= self.FINAL_INDEX_FILE_CAP):
            # If the final index is full or it's the last index, dump it to a file.
            self._dump_final_inverted_index_to_file()

    def merge_temp_indexes(self):
        print("Primary Index Merging Started")
        temp_index_fp_list = []
        temp_inverted_idx = {}
        
        cur_word = ""
        cur_doc_count = 0
        cur_word_freq = 0
        cur_posting_list = ""

        min_heap = []

        # Open temporary index files and initialize the min heap.
        for idx in range(self.temp_index_file_count):
            temp_index_file_name = "temp_index_" + str(idx) + ".txt"
            temp_index_fp = open(os.path.join(self.INDEX_FOLDER_PATH, temp_index_file_name), "r", encoding='utf-8')
            temp_index_fp_list.append(temp_index_fp)
            line = temp_index_fp_list[idx].readline().strip("\n")
            if(line != ""):
                word, doc_count, word_freq, posting_list = line.split("=")
                temp_inverted_idx[idx] = {"doc_count": int(doc_count), "total_count": int(word_freq), "posting_list": posting_list}
                min_heap.append((word, idx))
            else :
                temp_index_fp_list[idx].close()

        heapq.heapify(min_heap)

        while(len(min_heap) > 0) :
            word, idx = heapq.heappop(min_heap)
            if(word == cur_word):
                cur_doc_count += temp_inverted_idx[idx]["doc_count"]
                cur_word_freq += temp_inverted_idx[idx]["total_count"]
                cur_posting_list += "|" + temp_inverted_idx[idx]["posting_list"]
            else:
                if(cur_word != ""):
                    # Add the current word's data to the final inverted index.
                    self._add_final_inverted_index(cur_word, cur_doc_count, cur_word_freq, cur_posting_list)
                    if(self.total_unique_words % 1000 == 0):
                        print("Words Processed :", self.total_unique_words, end = "\r")
                cur_word = word
                cur_doc_count = temp_inverted_idx[idx]["doc_count"]
                cur_word_freq = temp_inverted_idx[idx]["total_count"]
                cur_posting_list = temp_inverted_idx[idx]["posting_list"]

            line = temp_index_fp_list[idx].readline().strip("\n")
            if(line != ""):
                word, doc_count, word_freq, posting_list = line.split("=")
                temp_inverted_idx[idx] = {"doc_count": int(doc_count), "total_count": int(word_freq), "posting_list": posting_list}
                heapq.heappush(min_heap, (word, idx))
            else :
                temp_index_fp_list[idx].close()
        
        # Add the final word's data to the final inverted index.
        self._add_final_inverted_index(cur_word, cur_doc_count, cur_word_freq, cur_posting_list)
        print("Words Processed :", self.total_unique_words)
        
        # Mark the end of the final index.
        self._add_final_inverted_index(word = None, doc_count = None, word_freq = None, posting_list = None, isLast = True)
        print("Primary Index Merging Completed")
