# WikiSearch: Wikipedia_Search_Engine

## Description

* Implemented a search engine on the Wikipedia dump of size 90 GB. To retrieve results faster and more relevant, indexing and ranking are implemented. A relevance ranking algorithm is implemented using the TF-IDF score to rank documents. Creating an index takes around 16 hr on a given Wikipedia dump. The result is retrieved in less than 2 seconds.

## Prerequisites

* python3
* For preprocessing, stop_word removal, and Stemming, I have used nltk library.
* To install nltk `pip3 install nltk`


### Directory_structure:
```
WikiSearch
|____ README.md
|____ src
      |____ invertedIndexHandler.py
      |____ preprocessor.py
      |____ secondaryIndexHandler.py
      |____ titleHandler.py
      |____ wikiHandler.py
      |____ wikiIndexer.py
      |____ wikiSearch.py
```

## How to run:

- Indexing
    ```
    cd src
    python3 wikiIndexer.py <path_to_wiki_dump> <path_to_inverted_index> <stat_file_name>
    ```

- Searching
    ```
    cd src
    python3 wikiSearch.py <path_to_inverted_index> <query_file_path> <is_interavtive_mode>
    ```

# Format of the query

* It supports two types of query.
* Normal query e.g. `new york`, `gandhi`, `1981 world cup`
* Field query e.g. `title:gandhi body:arjun infobox:gandhi category:gandhi ref:gandhi`
* Top 10 results will be printed.

