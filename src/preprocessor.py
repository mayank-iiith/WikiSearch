import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords as STOP_WORDS
from nltk import word_tokenize

class Preprocessor:
    def __init__(self, MAX_WORD_CAP):
        self.MAX_WORD_CAP = MAX_WORD_CAP
        self.stopwords = set(STOP_WORDS.words('english'))
        self.stemmer = PorterStemmer()
        self.TotalWordsEncountered = 0

        self.externalLinksPattern = r"==External links==\n[\s\S]*?\n\n"
        self.referencesPattern = r"== ?references ?==(.*?)\n\n"
        self.removeSymbolsPattern = r"[~`!@#$%-^*+{\[}\]\|\\<>/?]"

        self.filters = set(['(', '{', '[', ']', '}', ')', '=', '|', '?', ',', '+', '\'', '\\', '*', '#', ';', '!', '\"', '%'])

        self.wiki_pattern = {
            "infobox" : "{{infobox",
            "category" : "\[\[category:\s*(.*?)\]\]",
            "external_links": r"==External links==\n[\s\S]*?\n\n",
            # "comments" : "<--.*?-->",
            # "styles" : "\[\|.*?\|\]",
            # "references": "<ref>.*?</ref>",
            "curly_braces": "{{.*?}}",
            "square_braces": "\[\[.*?\]\]",
            "url": "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),# ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            "www": "www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        }

    def _remove_all_tags(self, text):
        tag_regex = re.compile("<.*?>")
        return re.sub(tag_regex, '', text)

    def _remove_all_urls(self, text):
        regex = re.compile(self.wiki_pattern["url"])
        text = re.sub(regex, ' ', text)
        regex = re.compile(self.wiki_pattern["www"])
        text = re.sub(regex, ' ', text)
        return text

    def _filter_content(self, text):
        for f in self.filters:
            text = text.replace(f, ' ')
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def _strip_footers(self, text):
        labels = ["references", "further reading", "see also", "notes"]
        for label in labels:
            regex = "== %s ==" % (label)
            found = re.search(regex, text, flags= re.IGNORECASE)
            if found is not None:
                text = text[0:found.start()-1]
        return text

    def _extract_infobox_content(self, text):
        if(len(text) == 0):
            return text, ""
        
        start_idx = text.find(self.wiki_pattern['infobox'])
        if(start_idx < 0): 
            return text, ""
            
        pattern_len = len(self.wiki_pattern['infobox'])
        end_idx = len(text)
        bracket_cnt = 2

        for idx in range(start_idx + pattern_len, end_idx):
            if(text[idx] == '{'):
                bracket_cnt += 1
            elif(text[idx] == '}'):
                bracket_cnt -= 1
            elif(bracket_cnt == 0):
                break

        text = text[0: start_idx - 1] + text[idx: -1]
        infobox_content = text[start_idx: idx - 2]
        infobox_content = self._remove_all_urls(infobox_content)
        infobox_content = self._filter_content(infobox_content)
        infobox_content = self._remove_all_tags(infobox_content)
        return text, infobox_content
    
    def _extract_category_content(self, text):
        category_regex = re.compile(self.wiki_pattern['category'], flags= re.IGNORECASE)
        category_content = re.findall(category_regex, text)
        category_content = ' '.join(category_content)
        category_content = self._remove_all_urls(category_content)
        category_content = self._filter_content(category_content)
        category_content = self._remove_all_tags(category_content)
        text = re.sub(category_regex, ' ', text)
        return text, category_content

    def _extract_external_links_content(self, text):
        external_links_regex = re.compile(self.externalLinksPattern, flags= re.IGNORECASE)
        external_links_content = re.findall(external_links_regex, text)
        external_links_content = ' '.join(external_links_content)
        external_links_content = external_links_content[20:]
        external_links_content = re.sub('[|]', ' ', external_links_content)
        external_links_content = re.sub('[^a-zA-Z ]', ' ', external_links_content)
        text = re.sub(external_links_regex, ' ', text)
        return text, external_links_content

    def _extract_references_content(self, text):
        references_regex = re.compile(self.referencesPattern, flags = re.DOTALL | re.MULTILINE | re.IGNORECASE)
        references_content = re.findall(references_regex, text)
        references_content = ' '.join(references_content)
        references_content = re.sub(self.removeSymbolsPattern, ' ', references_content)
        text = re.sub(references_regex, ' ', text)
        return text, references_content    

    def _extract_body_content(self, text):
        body_content = text
        regex = re.compile(self.wiki_pattern["curly_braces"])
        body_content = re.sub(regex, ' ', body_content)
        regex = re.compile(self.wiki_pattern["square_braces"])
        body_content = re.sub(regex, ' ', body_content)
        body_content = self._remove_all_tags(body_content)
        body_content = self._remove_all_urls(body_content)
        body_content = self._strip_footers(body_content)
        return body_content
    
    def _process(self, text):
        text = self._filter_content(text).lower()

        # Tokenization of text
        tokenized_text = word_tokenize(text)
        
        # for stat
        self.TotalWordsEncountered += len(tokenized_text)
        
        # Removing the stopwords, and words of size more than capacity.
        processed_text = [word for word in tokenized_text if len(word) < self.MAX_WORD_CAP and word not in self.stopwords]

        #stemming of words
        stemmed_text = [self.stemmer.stem(word) for word in processed_text]
        return stemmed_text

    def process_title(self, raw_title):
        return self._process(raw_title)

    def process_text(self, raw_text):
        raw_text = raw_text.lower()
        raw_text, raw_infobox = self._extract_infobox_content(raw_text)
        raw_text, raw_category = self._extract_category_content(raw_text)
        raw_text, raw_external_links = self._extract_external_links_content(raw_text)
        raw_text, raw_references = self._extract_references_content(raw_text)
        raw_body = self._extract_body_content(raw_text)
        return self._process(raw_infobox), self._process(raw_body), self._process(raw_category), self._process(raw_external_links), self._process(raw_references)
