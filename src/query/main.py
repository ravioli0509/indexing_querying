import sys
import json
from query import query_word
import timeit
import os

if __name__ == "__main__":
    start = timeit.default_timer()
    if len(sys.argv) == 3:
        query = sys.argv[2]
        directory = sys.argv[1]
        # Error Handling
        if (os.path.exists(str(directory))):
           result = query_word(query.lower())
           print("====RESULT====")
           print("Found Posting List: "+str(result))
        else:
            print("[ERROR]: Directory Doesnt Exist")
    else:
        print("[ERROR]: Not Enough Arguments")
    stop = timeit.default_timer()
    print('TIME (sec): ', stop - start)