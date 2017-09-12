import bs4
import urllib
from bs4 import BeautifulSoup
import argparse
import re
from sqlalchemy import *

DATABASEURI = "postgresql://user:password@35.185.80.xxx/w4111"

def main(url, tid, type='text', delimiter=' '):
    try:
        page = urllib.urlopen(url)
    except Exception as e:
        print("Error opening url: {}\nMessage:{}\n".format(url, e))

    soup = BeautifulSoup(page, 'lxml')
    contents = delimiter.join([p.text for p in soup.findAll('p')])

    engine = create_engine(DATABASEURI)
    with engine.connect() as conn:
        if type == 'text':
            sqlcmd = "UPDATE teams \
                    SET wiki_text=\'{}\' \
                    WHERE tid={}".format(
                    re.sub(r'[\'\"%]', '', contents.encode('ascii', 'ignore')), 
                    tid)
        else:
            sqlcmd = "UPDATE teams \
                    SET wiki_vector=to_tsvector('english', \'{}\') \
                    WHERE tid={}".format(
                    re.sub(r'[\'\"%]', '', contents.encode('ascii', 'ignore')), 
                    tid)

        try:
            cursor = conn.execute(sqlcmd)
            cursor.close()
        except Exception as e:
            print("Error executing SQL command. Message:\n{}\n".format(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='extract plain text from web page')
    parser.add_argument('url', type=str, help='url of web page')
    parser.add_argument('tid', type=int, help='team ID in database')
    parser.add_argument('--type', type=str, default='text', help='tsvector?text(default)?')
    parser.add_argument('--delimiter', default=' ', help='delimiter that separates paragraphs in output')
    
    args = vars(parser.parse_args())

    main(**args)

