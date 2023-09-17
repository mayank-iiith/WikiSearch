import os
import sys
from datetime import datetime

from secondaryIndexHandler import SecondaryIndexHandler
from titleHandler import TitleHandler
from preprocessor import Preprocessor

# Global Variables
INDEX_FOLDER_PATH = "indexFolder"

MAX_WORD_CAP = 30
TITLE_FILE_CAP = 20000
k = 10
section_weight = [1.0, 0.65, 0.05, 0.15, 0.2, 0.175]

short_field_replace = {
    "title:" : ";t:",
    "infobox:" : ";i:",
    "body:" : ";b:",
    "category:" : ";c:",
    "links:" : ";l:",
    "reference:" : ";r:"
}

field_mapping = {
    "t" : 0,
    "i" : 1,
    "b" : 2,
    "c" : 3,
    "l" : 4,
    "r" : 5
}

secondaryIndexHandler = None
preprocessor = None
titleHandler = None


def extract_field_count(posting_list):
    # Extract field counts from a posting list.
    fields = [0, 0, 0, 0, 0, 0]
    posting_list = posting_list.split("-")
    for posting in posting_list:
        if(posting[0] == 't'):
            fields[0] = int(posting[1:])
        elif(posting[0] == 'i'):
            fields[1] = int(posting[1:])
        elif(posting[0] == 'b'):
            fields[2] = int(posting[1:])
        elif(posting[0] == 'c'):
            fields[3] = int(posting[1:])
        elif(posting[0] == 'l'):
            fields[4] = int(posting[1:])
        elif(posting[0] == 'r'):
            fields[5] = int(posting[1:])
    return fields
    
def get_fields_score(fields, IDF, field = None):
    # Calculate the score for a given set of fields.
    score = 0
    for i in range(0, len(fields)):
        if field is None:
            score += (float(fields[i]) * float(section_weight[i]) * float(IDF))
        elif(i == field):
            score += (float(fields[i]) * float(IDF))
    return score

def get_word_scores(word, field = None):
    # Retrieve the scores for a word in a specific field.
    index_file_idx = secondaryIndexHandler.get_index_file_idx(word)
    index_file_name = "index_" + str(index_file_idx) + ".txt"
    with open(os.path.join(INDEX_FOLDER_PATH, index_file_name), "r", encoding='utf-8') as index_fp:
        score = {}
        line = index_fp.readline()
        while(line != ""):
            line = line.strip("\n")
            if(line != ""):
                cur_word, idf, doc_count, word_freq, posting_list = line.split("=")
                if(cur_word == word) :
                    docs = posting_list.split("|")
                    for doc in docs:
                        docID, posting_list = doc.split(" ")
                        fields = extract_field_count(posting_list)
                        cur_score = get_fields_score(fields, idf, field)
                        if cur_score > 0:
                            score[int(docID)] = cur_score
            line = index_fp.readline()
    return score

def process_non_field_query(query):
    # Process a non-field query and retrieve the top-k documents.
    words = preprocessor.process(query)
    docs_scores = {}
    for word in words:
        word_scores = get_word_scores(word)
        for docID, score in word_scores.items():
            if docID not in docs_scores:
                docs_scores[docID] = score
            else:
                docs_scores[docID] += score
    docs_scores_sorted = sorted(docs_scores.items(), key=lambda x: x[1], reverse=True)
    top_k_docs = [item[0] for item in docs_scores_sorted[:k]]
    return top_k_docs

def process_field_query(query):
    # Process a field query and retrieve the top-k documents.
    query = query.lower()
    for field, short_field in short_field_replace.items():
        query = query.replace(field, short_field)

    query = query.split(";")[1:]
    
    field_query = [[], [], [], [], [], []]
    for q in query:
        field, words = q.split(":")
        words = preprocessor.process(words)
        field_query[field_mapping[field]] += words

    docs_scores = {}
    for i in range(6):
        for word in field_query[i]:
            word_scores = get_word_scores(word, i)
            for docID, score in word_scores.items():
                if docID not in docs_scores:
                    docs_scores[docID] = score
                else:
                    docs_scores[docID] += score
    docs_scores_sorted = sorted(docs_scores.items(), key=lambda x: x[1], reverse=True)
    top_k_docs = [item[0] for item in docs_scores_sorted[:k]]
    return top_k_docs

def process_query(query):
    # Process a query, whether it's fielded or non-fielded.
    start_query_time = datetime.utcnow()
    if ":" in query:
        top_k_docs = process_field_query(query)
    else:
        top_k_docs = process_non_field_query(query)
    topK_docs_details = []
    for docID in top_k_docs:
        title = titleHandler.get_title(docID)
        topK_docs_details.append((docID, title))
    end_query_time = datetime.utcnow()
    query_processing_time = (end_query_time - start_query_time).total_seconds()
    return topK_docs_details, query_processing_time

def start_interactive(query):
    # Start interactive mode and process user queries.
    top_docs, query_processing_time = process_query(query)
    print("----------------------------------------------------------")
    print("Query: '" + query + "'")
    for docID, doc_title in top_docs:
        print(str(docID) + ", " + doc_title)
    print("Processing Time: %.2f seconds" % query_processing_time)
    print("----------------------------------------------------------")

def non_interactive(query_in_file_name):
    # Process queries from a file and write results to an output file.
    start_time = datetime.utcnow()

    with open(query_in_file_name, "r", encoding='utf-8') as query_in_fp:
        queries = query_in_fp.readlines()
        queries = [query.strip("\n").strip(" ") for query in queries if query.strip("\n").strip(" ") != ""]

    query_out_file_name = "query_out.txt"

    with open(query_out_file_name, "w", encoding='utf-8') as query_out_fp:
        query_out_fp.write("----------------------------------------------------------\n")
        for query in queries:
            top_docs, query_processing_time = process_query(query)
            query_out_fp.write("Query: '" + query + "'\n")
            for docID, doc_title in top_docs:
                query_out_fp.write(str(docID) + ", " + doc_title + "\n")
            query_out_fp.write("Processing Time: %.2f seconds\n" % query_processing_time)
            query_out_fp.write("----------------------------------------------------------\n")

        end_time = datetime.utcnow()
        total_processing_time = (end_time - start_time).total_seconds()
        query_out_fp.write("Total Processing Time: %.2f seconds\n" % total_processing_time)
        query_out_fp.write("----------------------------------------------------------\n")

    print("Queries Executed Successfully in %.2f seconds" % total_processing_time)
    print("Queries output written to the file '" + query_out_file_name + "'")


if __name__ == "__main__":
    if(len(sys.argv) != 4):
        print("Invalid number of arguments")
        print("Expected 3 arguments: <path_to_wiki_xml_dump> <path_to_index_folder> <stat_file_name>")
        exit(1)

    # global WIKI_DUMP_XML_FILE_PATH, INDEX_FOLDER_PATH, STAT_FILE_NAME
    IS_INTERACTIVE = False

    INDEX_FOLDER_PATH = os.path.abspath(sys.argv[1])
    IS_INTERACTIVE = sys.argv[3].lower()
    QUERY_IN = sys.argv[2]

    
    print(INDEX_FOLDER_PATH, QUERY_IN, IS_INTERACTIVE)
    
    preprocessor = Preprocessor(MAX_WORD_CAP)
    titleHandler = TitleHandler(INDEX_FOLDER_PATH, TITLE_FILE_CAP)

    # Loading Secondary Index
    secondaryIndexHandler = SecondaryIndexHandler(INDEX_FOLDER_PATH)
    secondaryIndexHandler.load_secondary_index()

    if(IS_INTERACTIVE == "true"):
        start_interactive(QUERY_IN)
    else:
        non_interactive(QUERY_IN)

