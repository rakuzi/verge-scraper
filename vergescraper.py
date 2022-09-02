import logging
import sqlite3
import datetime
import csv
import feedparser


class RSSItem:

    def __init__(self, title, author, link, published):
        self.title = title
        self.author = author
        self.link = link
        self.published = published


class RSSReader:
    
    def __init__(self, feed_url):
        self.feed_url = feed_url

    def get_data(self):
        return feedparser.parse(self.feed_url)


    def get_rss_objects(self):
        feed = self.get_data()
        rss_objects = []
        for entry in feed.entries:
            obj = RSSItem(
                    title=entry.title,
                    author=entry.author,
                    link=entry.link,
                    published=entry.published[:10],
                )
            rss_objects.append(obj)
        return rss_objects


class Database:

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

    def execute(self, query, data):
        self.cur.execute(query, data)
        self.conn.commit()
        return self.cur

    def create_table(self):
        return self.execute("""CREATE TABLE IF NOT EXISTS articles(
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE,
            headline TEXT,
            author TEXT,
            date TEXT
        )
        """, ())

    def add_article(self, data):
        return self.execute("""
            INSERT INTO articles VALUES(?, ?, ?, ?, ?)
            """, data)



if __name__ == '__main__':
    logging.basicConfig(filename="error.log", level=logging.ERROR)

    # setup database
    db = Database('articles.db')
    db.create_table()

    # get articles from theverge.com
    rss_objects = RSSReader("https://www.theverge.com/rss/index.xml").get_rss_objects()

    # # csv filename in 'ddmmyyyy_verge.csv' format
    current_date = datetime.date.today().strftime('%d%m%Y')
    csv_filename = f'{current_date}_verge.csv'
    
    # # write data to csv file
    with open(csv_filename, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['id', 'url', 'headline', 'author', 'date'])

        for i, obj in enumerate(rss_objects):
            csv_writer.writerow([i, obj.link, obj.title, obj.author, obj.published])


    # database handling
    with open(csv_filename, newline='') as f:
        rows = csv.reader(f)
        headers = next(rows)
        for row in rows:
            try:
                if row:
                    db.add_article(row)
            except Exception as e:
                logging.error(e)
