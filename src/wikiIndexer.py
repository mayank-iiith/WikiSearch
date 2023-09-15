# Libraries
import xml.sax
import os
import sys
from datetime import datetime

from wikiHandler import WikiHandler
from secondaryIndexHandler import SecondaryIndexHandler

# Global Variables
WIKI_DUMP_XML_FILE_PATH = "wikiDump.xml"
INDEX_FOLDER_PATH = "indexFolder"
STAT_FILE_NAME = "fileStat.txt"


MAX_WORD_CAP = 30
TITLE_FILE_CAP = 2000
INVERTED_INDEX_TEMP_FILE_CAP = 1000000
FINAL_INDEX_FILE_CAP = 1000000
STATS = {}


def convertSize(fileSize):
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024
    convertedSize = ""
    if(fileSize >= GB) :
       convertedSize = "%.2f GB" % (fileSize/GB)
    elif(fileSize >= MB):
       convertedSize = "%.2f MB" % (fileSize/MB)
    elif(fileSize >= KB):
       convertedSize = "%.2f KB" % (fileSize/KB)
    else:
        convertedSize = "%.2f B" % (fileSize)
    return convertedSize

def get_index_size():
    index_size = 0
    for file in os.listdir(INDEX_FOLDER_PATH):
        if(file.startswith("index_") or file.startswith("secondary_index") or file.startswith("title")):
            fp = os.path.join(INDEX_FOLDER_PATH, file)
            size = os.path.getsize(fp)
            index_size += size
    return convertSize(index_size)


def generate_statistics():
    global STAT_FILE_NAME
    with open(STAT_FILE_NAME, "w", encoding='utf-8') as stat_fp:
        stat_fp.write("Total Documents: \t\t\t\t" + str(STATS["TotalDocCount"]) + "\n")
        stat_fp.write("Total Tokens Encountered: \t\t" + str(STATS["TotalWordsEncountered"]) + "\n")
        stat_fp.write("Total Tokens Indexed: \t\t\t" + str(STATS["TotalWords"]) + "\n")
        stat_fp.write("Total Unique Tokens: \t\t\t" + str(STATS["TotalUniqueWords"]) + "\n")
        stat_fp.write("Title File Count: \t\t\t\t" + str(STATS["TitleFileCount"]) + "\n")
        stat_fp.write("Primary Index File count: \t\t" + str(STATS["PrimaryIndexFileCount"]) + "\n")
        stat_fp.write("Secondary Index File count: \t" + str(STATS["SecondaryIndexFileCount"]) + "\n")
        stat_fp.write("Index Size: \t\t\t\t\t" + str(STATS["IndexSize"]) + "\n")
        stat_fp.write("Primary Index Creation Time: \t" + str(STATS["PrimaryIndexTime"]) + "\n")
        stat_fp.write("Secondary Index Creation Time: \t" + str(STATS["SecondaryIndexTime"]) + "\n")


def purgeFiles(folderName, fileNamePrefix) :
    for file in os.listdir(folderName):
        if file.startswith(fileNamePrefix):
            os.remove(os.path.join(folderName, file))


if __name__ == "__main__":
    if(len(sys.argv) != 4):
        print("Invalid number of arguments")
        print("Expected 3 arguments: <path_to_wiki_xml_dump> <path_to_index_folder> <stat_file_name>")
        exit(1)

    # global WIKI_DUMP_XML_FILE_PATH, INDEX_FOLDER_PATH, STAT_FILE_NAME

    WIKI_DUMP_XML_FILE_PATH = os.path.abspath(sys.argv[1])
    INDEX_FOLDER_PATH = os.path.abspath(sys.argv[2])
    STAT_FILE_NAME = sys.argv[3]

    if(not os.path.isfile(WIKI_DUMP_XML_FILE_PATH)):
        print("Invalid wiki xml file path")
        exit(1)

    if(not os.path.isdir(INDEX_FOLDER_PATH)):
        print("Index folder doesn't exist, creating index folder : '", sys.argv[2], "'", sep = '')
        os.mkdir(INDEX_FOLDER_PATH)

    
    purgeFiles(INDEX_FOLDER_PATH, "title_")
    purgeFiles(INDEX_FOLDER_PATH, "temp_index_")
    purgeFiles(INDEX_FOLDER_PATH, "index_")
    purgeFiles(INDEX_FOLDER_PATH, "secondary_index_")
    purgeFiles("./", STAT_FILE_NAME)

    start_time = datetime.utcnow()

    # create a WikiHandler object
    wikiHandler = WikiHandler(INDEX_FOLDER_PATH, MAX_WORD_CAP, TITLE_FILE_CAP, INVERTED_INDEX_TEMP_FILE_CAP, FINAL_INDEX_FILE_CAP)

    # parsing xml wiki dump file & Building Primary Index
    wikiParser = xml.sax.make_parser()
    wikiParser.setFeature(xml.sax.handler.feature_namespaces, 0)
    wikiParser.setContentHandler(wikiHandler)
    wikiParser.parse(WIKI_DUMP_XML_FILE_PATH)

    purgeFiles(INDEX_FOLDER_PATH, "temp_index_")
    primary_end_time = datetime.utcnow()

    STATS["TotalDocCount"] = wikiHandler.TotalDocCount
    STATS["TotalWordsEncountered"] = wikiHandler.TotalWordsEncountered
    STATS["TotalWords"] = wikiHandler.TotalWords
    STATS["TotalUniqueWords"] = wikiHandler.TotalUniqueWords
    STATS["TitleFileCount"] = wikiHandler.TitleFileCount
    STATS["PrimaryIndexFileCount"] = wikiHandler.PrimaryIndexFileCount
    STATS["PrimaryIndexTime"] = (primary_end_time - start_time).total_seconds()
    print("Primary Index creation time:", STATS["PrimaryIndexTime"], "seconds")

    # Building Secondary Index
    secondaryIndexHandler = SecondaryIndexHandler(INDEX_FOLDER_PATH)
    secondaryIndexHandler.build_secondary_index()
    secondary_end_time = datetime.utcnow()

    STATS["SecondaryIndexFileCount"] = secondaryIndexHandler.SecondaryIndexFileCount
    STATS["SecondaryIndexTime"] = (secondary_end_time - primary_end_time).total_seconds()
    print("Secondary Index creation time:", STATS["SecondaryIndexTime"], "seconds")

    STATS["IndexSize"] = get_index_size()
    generate_statistics()
