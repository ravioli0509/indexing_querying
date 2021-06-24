import nltk
import string
import re
import csv

ZONE_1 = {}
ZONE_2 = {}


def clean_text(text):
    temp_result = text.translate ({ord(c): " " for c in "!£@#$%^&−*()[]{};:…,./…—<>?\|~-=_+–”‘“"})
    temp_result_2 = temp_result.translate ({ord(c): " " for c in "°'`’"}) ## convert any word like can't to cant it`s to its
    last_temp = temp_result_2.translate(str.maketrans('','', string.punctuation))
    result = re.sub(' +', ' ', last_temp) ## get rid of extra space
    return result


def indexing(json_data, doc_id, zone_1, zone_2):
    for i in range(0, len(json_data)):
        '''
            Text normalization, unnecessary characters and spaces are swept
            All text become lower
        '''
        review_clean = clean_text(json_data[i][zone_1])

        posting_id = int(json_data[i][doc_id])
      
        '''
            tokenize each text
        '''
        review_tokenize = nltk.word_tokenize(review_clean)
        sorted_review = sorted([word.lower() for word in review_tokenize])

        '''
            Creates a hashmap of word frequency for currenct doc 
        '''

        wordfreq_zone_1 = {}
        wordfreq_zone_2 = {}


        '''
         -- Algo --
            It checks for unique word in the global hash map, 
            If the word is not in the first hash map, Initializes as { 'new_word': [0 (df), [empty posting list]] }

            Update the values of frequency and list of posting id
        '''

        for word in sorted_review:
            if word not in wordfreq_zone_1:
                wordfreq_zone_1[word] = 0
            wordfreq_zone_1[word] += 1
        
        for word in wordfreq_zone_1:
            if word not in ZONE_1:
                ZONE_1[word] = [0, []]
            ZONE_1[word][0] += wordfreq_zone_1[word]
            ZONE_1[word][1].append(posting_id)

        '''
            Same algorithm flow goes with for zone 2
        '''

        title_clean = clean_text(json_data[i][zone_2])
        title_tokenize = nltk.word_tokenize(title_clean)
        sorted_title = sorted([word.lower() for word in title_tokenize])


        for word in sorted_title:
            if word not in wordfreq_zone_2:
                wordfreq_zone_2[word] = 0
            wordfreq_zone_2[word] += 1

        for word in wordfreq_zone_2:
            if word not in ZONE_2:
                ZONE_2[word] = [0, []]
            ZONE_2[word][0] += wordfreq_zone_2[word]
            ZONE_2[word][1].append(posting_id)

    sorted_zone_1, sorted_zone_2 = sort_zones(ZONE_1, ZONE_2)
    
    return sorted_zone_1, sorted_zone_2
    

def sort_zones(ZONE_1, ZONE_2):
    '''
        Sort the zones
    '''
    temp_1 = {}
    temp_2 = {}
    for key in sorted(ZONE_1):
        temp_1[key] = ZONE_1[key]
    
    for key in sorted(ZONE_2):
        temp_2[key] = ZONE_2[key]

    return temp_1, temp_2

def write_csv(tsv_dir, zone_1, zone_2, zone_id_1, zone_id_2):
    '''
        Csv write up, using user input stores in right folder
    '''
    with open(tsv_dir+zone_id_1+'.csv', 'w') as f_1:
        writer = csv.writer(f_1)
        writer.writerow(["Token","FD","Posting"])
        for word in zone_1:
            writer.writerow([word, zone_1[word][0], zone_1[word][1]])
        f_1.close()

    with open(tsv_dir+zone_id_2+'.csv', 'w') as f_2:
        writer = csv.writer(f_2)
        writer.writerow(["Token","FD","Posting"])
        for word in zone_2:
            writer.writerow([word, zone_2[word][0], zone_2[word][1]])
        f_2.close()