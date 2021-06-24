import sys
import json
from index import write_csv, indexing
import timeit
import os

if __name__ == "__main__":
    '''
        handling user inputs
        and error handlings.
    '''
    start = timeit.default_timer()
    if len(sys.argv) == 3:
        file = sys.argv[1]
        tsv_dir = sys.argv[2]
        with open('data/'+file) as json_data:
            data = json.load(json_data)
            zone_keys = []
            for i in data[0]:
                zone_keys.append(i)
            print("Indexing: "+file)
            zone_id_1 = str(zone_keys[1])
            zone_id_2 = str(zone_keys[2])
            zone_1, zone_2 = indexing(data, str(zone_keys[0]), zone_id_1, zone_id_2)
            if not (os.path.exists(str(tsv_dir))):
                try:
                    os.makedirs(str(tsv_dir))
                except OSError:
                    print ("[ERROR]: Creation of the directory %s failed" % str(tsv_dir))

            write_csv(tsv_dir, zone_1, zone_2, zone_id_1, zone_id_2)
        json_data.close()
    else:
        print("[ERROR]: Not Correct Number of Arguments")
    stop = timeit.default_timer()
    print('TIME: ', stop - start)
