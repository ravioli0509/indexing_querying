import csv
import boolean
import sys
import re
from shuntingyard import shunting_yard
import ast
import os
import timeit
import itertools

ALL_SHORT = []
ALL_LONG = []

def query_word(query_arg):
    '''
        Parsed the query using boolean.py 
        Applies string conversions to add space for shunting yard algo
        When the query only has one token it will simpliy find token from file
        If it was negation of single token, then it would get all the postings and computes not_and_query
    '''
    LONG = True if 'book' in query_arg or 'line' in query_arg else False
    SHORT = True if 'title' in query_arg or 'review' in query_arg else False
    
    parsed_query = ''
    try:
        algebra = boolean.BooleanAlgebra()
        parsed_query = algebra.parse(query_arg)
    except:
        print("[ERROR]: Wrong Query Syntax, Try again")
        sys.exit()
    operators = ["&", "|"]
    query = str(parsed_query)

    for i in query:
        if i in operators:
           query = query.replace(i, ' '+i+' ')

    '''
        Singleton Operation
    '''
    c = clean_query(query)
    if len(c) == 1:
        t = c[0]
        if '~' in t:
            token = t.split('~')[1]
            all_l, all_s = get_all_postings(LONG, SHORT)
            posting = get_postings(token)
            if SHORT:
                return and_not_query(all_s, posting)
            else:
                return and_not_query(all_l, posting)
        else:
            return get_postings(t)

    return shunting_yard(c)


def or_query(posting_1, posting_2):
    '''
        Algorithm Taken From First Week Of Lecture Notes - Under Union of Posting Lists - Page 35
        https://eclass.srv.ualberta.ca/pluginfile.php/6875918/mod_resource/content/0/01_intro_2up.pdf
    '''

    p_1 = 0
    p_2 = 0
    result = []
    '''
        While posting_1 and posting_2 are not nil
        Equivalent to while if p_1 and p_2 exceeds the length of the postings
        If exceeds, we know its time to finish
    '''
    while p_2 < len(posting_2) and p_1 < len(posting_1):
        if posting_1[p_1] == posting_2[p_2]:
            result.append(posting_1[p_1]) ## appends if same
            p_1 = p_1 + 1
            p_2 = p_2 + 1
        elif posting_1[p_1] < posting_2[p_2]:
            result.append(posting_1[p_1])
            p_1 = p_1 + 1
        else:
            result.append(posting_2[p_2])
            p_2 = p_2 + 1

    # appends every other postings from p1 and p2
    while p_1 < len(posting_1):
        result.append(posting_1[p_1]) 
        p_1 = p_1 + 1
    
    while p_2 < len(posting_2):
        result.append(posting_2[p_2])
        p_2 = p_2 + 1

    return result

def and_query(posting_1, posting_2):
    '''
        Algorithm Taken From First Week Of Lecture Notes - Under Intersection of Posting Lists - Page 33
        https://eclass.srv.ualberta.ca/pluginfile.php/6875918/mod_resource/content/0/01_intro_2up.pdf
    '''
    p_1 = 0
    p_2 = 0
    result = []
    '''
        While posting_1 and posting_2 are not nil
        Equivalent to while if p_1 and p_2 exceeds the length of the postings
        If exceeds, we know its time to finish
    '''
    while p_1 < len(posting_1) and p_2 < len(posting_2):
        if posting_1[p_1] == posting_2[p_2]:
            result.append(posting_1[p_1]) ## if posting is the same append to result
            p_1 = p_1 + 1
            p_2 = p_2 + 1
        elif posting_1[p_1] < posting_2[p_2]:
            p_1 = p_1 + 1
        else:
            p_2 = p_2 + 1
    return result


def not_query(token, doc):
    '''
        Runs the And Not Query With All Postings
    '''
    posting_token = get_postings(token)
    if doc == 'book' or doc == 'line':
        _, all_s = get_all_postings(False, True)
        return and_not_query(all_s, posting_token)
    elif doc == 'title' or doc == 'review':
        all_l, _ = get_all_postings(True, False)
        return and_not_query(all_l, posting_token) 


def and_not_query(posting_1, posting_2):
    '''
        Algorithm Taken From First Week Of Lecture Notes - Under AND NOT of Posting Lists - Page 37
        https://eclass.srv.ualberta.ca/pluginfile.php/6875918/mod_resource/content/0/01_intro_2up.pdf
    '''
    p_1 = 0
    p_2 = 0
    results = []
    '''
        While posting_1 and posting_2 are not nil
        Equivalent to while if p_1 and p_2 exceeds the length of the postings
        If exceeds, we know its time to finish
    '''
    while p_1 < len(posting_1) and p_2 < len(posting_2):
        if posting_1[p_1] == posting_2[p_2]:
            p_1 = p_1 + 1
            p_2 = p_2 + 1
        elif posting_1[p_1] < posting_2[p_2]:
            results.append(posting_1[p_1])  # append result if p1 < p2
            p_1 = p_1 + 1
        else:
            p_2 = p_2 + 1

    while p_1 < len(posting_1):
        results.append(posting_1[p_1]) # append remaining p1 
        p_1 = p_1 + 1

    return results


def get_postings(token):
    zone_test = ['book', 'line', 'review', 'title']
    '''
        This function retrives posting lists of the token
        Prints an Error Message if token doesn't exists in the file
        Shuts the system down
    '''
    file, word = token.split(':')[0], token.split(':')[1]
    temp = []
    raw_data = []
    if file not in zone_test:
        print("[ERROR]: Zone Doesnt Exist")
        sys.exit()
    try:
        with open ('./'+sys.argv[1]+file+'.csv') as a:
            reader = csv.reader(a)
            raw_data = list(reader)
            del(raw_data[0])
            a.close()
    except:
        print("[ERROR]: File Doesnt Exist. Check if it exists")
    

    for data in raw_data:
        if data[0] == word:
            temp.append(ast.literal_eval(data[2]))
    

    result = clean_postings(temp)
    if len(result) == 0:
        print("[WARNING]: Error! No Token Was Found For: "+str(token))

    return result


def get_all_postings(LONG, SHORT):
    '''
        Getting all postings for each SHORT (from book or line) and LONG (from review or title)
        LONG and SHORT are booleans, it will be triggered if they are true
        This is for the negation query 

        Example if NOT(book:lorax)

        All postings from book (or line since they are same) AND NOT book:lorax
        Which becomes AND NOT QUERY

    '''
    global ALL_SHORT
    global ALL_LONG
    if SHORT and len(ALL_SHORT) == 0:
        try:
            with open ('./'+sys.argv[1]+'/book.csv') as a:
                reader = csv.reader(a)
                raw_data = list(reader)
                del(raw_data[0])
                for data in raw_data:
                    ALL_SHORT.append(ast.literal_eval(data[2]))
                ALL_SHORT = clean_postings(ALL_SHORT)
                a.close()
           
        except:
            print("Book File Doesnt Exist. Check if its indexed")

    if LONG and len(ALL_SHORT) == 0:
        try:
            with open ('./'+sys.argv[1]+'review.csv') as b:
                reader = csv.reader(b)
                raw_data = list(reader)
                del(raw_data[0])
                for data in raw_data:
                    ALL_LONG.append(ast.literal_eval(data[2]))
                ALL_LONG = clean_postings(ALL_LONG)
                b.close()

        except:
            print("Review File Doesnt Exist. Check if its indexed")
    
    return ALL_LONG, ALL_SHORT
    
def clean_postings(args):
    '''
        Cleans multidimensional list of posting lists
        Unflattens and remove duplicates
        Example [[0, 1, 2], [2, 3, 4, 5]] --> [0, 1, 2, 3, 4, 5]
    '''
    flattened = list(itertools.chain.from_iterable(args)) ## faster!!!
    flattened.sort()
    result = []
    [result.append(j) for j in flattened if j not in result]
    
    return result

def clean_query(e):
    '''
        Prepares ( ) separations for shunting yard algorithm
        After wards ~ will be merged with ( as ~(
    '''
    t = e.replace('(', ' ( ')
    s = t.replace(')', ' ) ')
    y = ' '.join(s.split(' ')).split()
    return y
