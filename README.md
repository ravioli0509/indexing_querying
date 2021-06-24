# Information Retrieval - Indexing & Querying

## Commands

- Most of the commands are done in Makefile. Hence it is important to put make in every command

```Makefile
    index-movies:
        python3 src/index/main.py movie_plots.json $(file_dir)

    index-seuss:
        python3 src/index/main.py dr_seuss_lines.json $(file_dir)

    query:
        python3 src/query/main.py $(file_dir) '$(query)'

    install:
        pip3 install -r requirements.txt

    download-nltk:
        python3 src/download_nltk.py
```
- Before running the program, we have to set up the environment, run the following commands

    1. `make install`
    2. `make download-nltk` - will take time 
    3. `make install` for good measure after installing nltk

## Running The Program 💻
- You will be running in the root directory of the project for querying and indexing.

- For Indexing Movie Plots
    - `make index-movies file_dir=${your_folder}`
    - Example would be `make index-movies file_dir=files/`
    - Or `python3 src/index/main.py movie_plots.json files/`

- For Indexing Dr. Seuss
    - `make index-seuss file_dir=${your_folder}`
    - Example would be `make index-seuss file_dir=files/`
    - Or `python3 src/index/main.py dr_seuss_lines_plots.json files/`

- Querying
    - `make query file_dir={same_as_above} query='YOUR QUERY' `
    - Example would be `make query file_dir=files/ query='line:you AND book:you AND NOT(book:Birthday)' `
    - Or `python3 src/query/main.py files/ 'line:you AND book:you AND NOT(book:Birthday)'`

## Algorithms Used 🧠

- Indexing
    - nltk.tokenization
    - Normalization
        - Words are lowered
        - Special characters are removed 
        - Words like It's was separated as it & s with space
        - Accents remain
        - Any integers remain, along with numbers and string comibation like '42nd'
    - Data Structure
        - For creating postings, dictionaries were used with hashing operations
        - If the word is not in the first hash map, Initializes as 
            `{ 'new_word': [0 (df), [empty posting list]] }`
        - Looped and updated
    - Storing in tsv
        - CSV files are used as storage files
        - Header written as `["Token","FD","Posting"]`
        - Rows are written as `[word, zone[word][0], zone[word][1]]`

- Querying
    - Algorithms Used
        - Shunting Yard Algorithm
        - AND_QUERY for boolean retrieval
        - OR_QUERY for boolean retrieval
        - NOT_AND_QUERY for boolean retrieval

    - Parsing Query
        - Boolean.py was used to stringify and parse the given query 
        - Example NOT(book:Lorax) AND line:you --> `~book:lorax & line:you`
        - String conversions were used to prepare for shunting yard algorithm
    
    - Query Optimization
        - Singleton queries weren't passed to shunting yard algorithm
        - NOT_AND_QUERY was used for negation of singleton negation
        - All postings list were retrieved once and kept in the global variables
        - Computes the queries in () first using the shunting yard algorithm

    - Shunting Yard
        - Heavily Tweaked From the General Algorithm
        - '~' and '(' are merged as one token --> When comes in contact we know theres a Negation of multiple expression
            - Example `~( A AND B OR C ) and D`

        -  ACTIVATE_NOT is here for handling ~( multiple boolean expresions ), handles for nested negations as well
            When the expression of sub-sequence of the expression is not wrapped around with NOT().
            When this node is activated, the inner expressions are handled, and then passed it to and_not_query
    
    - AND_QUERY, OR_QUERY, AND_NOT_QUERY
        - These algorithms were repeatedly used when evaluating two posting lists as operands when updating values in
          the shunting yard algorithm.
        - These algorithms can be found from [this lecture](https://eclass.srv.ualberta.ca/pluginfile.php/6875918/mod_resource/content/0/01_intro_2up.pdf)

    - Error Handling
        - Handles Error For
            - Syntax Error In Query
            - Wrong Number Of Arguments in Command Line
            - Warning For If Token Not Found
            - Wrong Zone Name Given
            - Folder Creation
            - Wrong Directory Given
            - Wrong File Names Given For Json


## References 📕
- Collaboration Done With Joe Heppelle (ccid: heppelle)
- Discussions were done based on the following topics
    - Evaluating the use of Shunting Yard Algorithms
        - Since we were handling order of operations on Boolean Expression, 
          we figured the infix expressions used in Boolean Expression is applicable
          in Shunting Yard Algorithm. The main operators were & and |, operands were operands like
          `book:lorax` or `~book:lorax`. 
        - Precedences were manually tweaked in order to compute `NOT( multiple expressions )` and other complex 
           expressions that required high level of order of operations
    - Give each other complex query and checking the results
    - Discussed about some efficient techniques in python that are mentioned in miscellaneous
        
### Boolean Query Algorithms
- [Lecture Slides By Denilson Barbosa @ University of Alberta](https://eclass.srv.ualberta.ca/pluginfile.php/6875918/mod_resource/content/0/01_intro_2up.pdf)

### Shunting Yard Algorithm
- [WIKIPEDIA](https://en.wikipedia.org/wiki/Shunting-yard_algorithm)
- [YOUTUBE](https://www.youtube.com/watch?v=QzVVjboyb0s)
- [BLOG](https://www.andr.mu/logs/the-shunting-yard-algorithm/)

### Miscellaneous
- Effiecient Python Methods
    - [Iterating To Flatten](https://docs.python.org/3/library/itertools.html)
    - [Converting Stringified List To Actual List](https://www.kite.com/python/docs/ast.literal_eval)

### NLTK
- [Website](https://www.nltk.org/)
### Boolean.py
- [Documentation](https://booleanpy.readthedocs.io/en/latest/users_guide.html#creating-boolean-expressions)

## Link To Video
[Video Link](https://drive.google.com/file/d/14Sc840cU6e9scE4R3Fs9Vtx_iuuyFNSo/view?usp=sharing)
