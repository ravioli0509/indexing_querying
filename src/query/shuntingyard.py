import query

ACTIVATE_NOT = False
TOTAL_DOCS = []

def mergeNotAndParanthese(tokens):
    '''
        This merges ~ and ( together as ~(, make it as one operator
        This will be done continuously until there is no single element of only ~
    '''
    while '~' in tokens:
        for i in range(0, len(tokens)-1):
            if tokens[i] == '~' and tokens[i+1] == '(':
                tokens[i:i+2] = [''.join(tokens[i:i+2])]     
                break
    return tokens

def pop_operator(stack):
    '''
        Same as pop method, but returns None if stack is empty
    '''
    return stack[-1] if stack else None
 
def evaluate_query(ops, values, all_postings):
    '''
        This query evalutes or so called computes the operations
        ACTIVATE_NOT is here for handling ~( multiple boolean expresions ), handles for nested negations as well
        When the expression of sub-sequence of the expression is not wrapped around with NOT() then usual operations will be done

        As it follows the shunting yard algorithm, any expression that should be computed in order comes in the function
    '''
    if ACTIVATE_NOT:

        if values[0] == 'start':
            operand = values.pop()
            if '~' in operand:
                s = operand.split('~')[1]
                doc = s.split(':')[0]
                operand = query.not_query(s, doc)

            values.append(query.and_not_query(all_postings, operand))
        else:
            operator = ops.pop()
            right = values.pop()
            left = values.pop()

            # computes Not(right) and Not(left) if ~ is there            
            if '~' in right and ':' in right:
                s = right.split('~')[1]
                doc = s.split(':')[0]
                right = query.not_query(s, doc)

            elif '~' in left and ':' in left:
                s = left.split('~')[1]
                doc = s.split(':')[0]
                left = query.not_query(s, doc)

            '''
                get posting results
            '''
            posting_right = query.get_postings(right) if ":" in right else right
            posting_left = query.get_postings(left) if ":" in left else left
            
            '''
                Run or_query or and_query
            '''
            if operator == "&":
                values.append(query.and_query(posting_left, posting_right))
            elif operator == "|":
                values.append(query.or_query(posting_left, posting_right))
    else:
        operator = ops.pop()
        right = values.pop()
        left = values.pop()

        '''
        #1 Handling NOT(a) if an expression like NOT(a) AND b occurs (applies to all kinds of expression)
        '''
        if '~' in right and ':' in right:
            s = right.split('~')[1]
            doc = s.split(':')[0]
            right = query.not_query(s, doc)

        elif '~' in left and ':' in left:
            s = left.split('~')[1]
            doc = s.split(':')[0]
            left = query.not_query(s, doc)

        '''
        #2 Getting postings of each operand from files. If operand is already in posting list, then skip
        '''
        posting_right = query.get_postings(right) if ":" in right else right
        posting_left = query.get_postings(left) if ":" in left else left

        '''
        #3 Handle inner operation, categorized by AND and OR. Store the resulting postings to values as memory
        '''
        if operator == "&":
            values.append(query.and_query(posting_left, posting_right))
        elif operator == "|":
            values.append(query.or_query(posting_left, posting_right))
    

def shunting_yard(tokens):
    '''
        Algorithm of Shunting Yard is Taken From Here
        - https://www.youtube.com/watch?v=QzVVjboyb0s
        - https://en.wikipedia.org/wiki/Shunting-yard_algorithm
    '''

    tokens = mergeNotAndParanthese(tokens) # Merge ~ and ( together if they are next to each other
    values = []
    ops = []
    '''
        Shunting Yard Parses the mathematical expression in infix notations and 
        compute the operations in order. 

        For this implementation, the logic in the algorithm is heavily tweaked in order to 
        compute negations that wrap around complex queries and nested negations with ().

    '''
    global TOTAL_DOCS
    global ACTIVATE_NOT
    counter = 0
    passed = 0

    for token in tokens:
        if ':' in token:
            '''
                Like the numbers in usual mathematical expressions, 
                doc:token will be the operands. This includes ~doc:token. 
            '''
            if ACTIVATE_NOT:
                '''
                    Enters Negation wrap NOT( ...enters here....)
                    long  -->  all postings from review.csv or title.csv
                    short --> all postings from book.csv or line.csv
                    Used for and_not_query
                '''
                if (('book' in token or 'line' in token) and 'short' not in TOTAL_DOCS):
                    TOTAL_DOCS.append('short')
                elif (('title' in token or 'review' in token) and 'long' not in TOTAL_DOCS):
                    TOTAL_DOCS.append('long')
            values.append(token)
        elif token == '(': 
            ops.append(token)
        elif token == '~(':
            '''
                Starting of Negation Wrapper. Negation Operation is Activated and ready 
                to be used when all operations are computed in wrapper
            '''
            ACTIVATE_NOT = True
            counter += 1
            tokens[tokens.index('~(')] = token.replace("~","")
            ops.append('(')
        elif token == ')':
            top = pop_operator(ops)
            while top is not None and top != '(':
                '''
                    Compute all queries inside ()
                '''
                evaluate_query(ops, values, all_postings=None)
                top = pop_operator(ops)
            if ACTIVATE_NOT:
                values.insert(0, 'start')
                '''
                    Compute NOT(result of queries)
                    Also computes nested negations, like NOT( NOT( ... ) )
                '''
                all_p = []
                passed += 1
                '''
                    Separate evalue query by all_postings
                    - merged list (both small and long)
                    - only small list (line or book)
                    - only long list (review or title)

                '''
                if 'short' in TOTAL_DOCS and 'long' in TOTAL_DOCS:
                    all_l, all_s = query.get_all_postings(True, True)
                    evaluate_query(ops, values, all_postings=query.clean_postings([all_l, all_s]))
                elif len(TOTAL_DOCS) == 1 and TOTAL_DOCS[0] == 'short':
                    _, all_s = query.get_all_postings(False, True)
                    evaluate_query(ops, values, all_postings=all_s)
                elif len(TOTAL_DOCS) == 1 and TOTAL_DOCS[0] == 'long':
                    all_l, _ = query.get_all_postings(True, False)
                    evaluate_query(ops, values, all_postings=all_l)
                '''
                    counter keeps track of how many times negation wrap is supposed to be done.
                    When its done --> ACTIVATE_NOT becomes false
                    Intializes counts of ~() and counter --> Ready to be used again when found 
                    again outside the wrapper
                '''
                values.pop(0)
                if counter == passed:
                    ACTIVATE_NOT = False
                    counter = 0
                    passed = 0

            ops.pop()
        
        else:
            '''
                When token is an operator
            '''
            top = pop_operator(ops)
            while top is not None and top not in '()':
                '''
                    If popped operator (top) is not a ( ), then we compute
                '''
                evaluate_query(ops, values, all_postings=None)
                top = pop_operator(ops)
            ops.append(token)
        '''
            Compute remaining operands and operators.
        '''
    while pop_operator(ops) is not None: 
        evaluate_query(ops, values, all_postings=None)
    
    return values[0]
