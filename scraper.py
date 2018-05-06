import time
import os
import glob
import json
import urllib
import re
from datetime import datetime, timedelta
import lxml.html
import dateutil.parser
from selenium import webdriver
from pprint import pprint
from selenium.webdriver.common.keys import Keys

#https://groups.google.com/forum/#!topicsearchin/alt.conspiracy/after$3A2018$2F03$2F01$20AND$20before$3A2018$2F04$2F01

CD = os.path.dirname(os.path.realpath(__file__))
GOOGLE_GROUP_BASE = 'https://groups.google.com/forum/'
SEARCH_URL = GOOGLE_GROUP_BASE + '#!topicsearchin/{group}/after$3A{after}$20AND$20before$3A{before}'
THREAD_URL = GOOGLE_GROUP_BASE + '#!topic/{group}/{hashcode}'
RETURN_HTML = "return document.getElementsByTagName('html')[0].innerHTML"
THREAD_DIRECTORY_FILENAME = os.path.join(CD, 'outputs', '{group}_threads_{after}-{before}.json')
POST_COUNT_REGEX = re.compile('([0-9]+) post')
SELECTORS = {'thread_url':    "//a[contains(@class, 'F0XO1GC-p-Q')]/@href",
             'thread_title':    "//a[contains(@class, 'F0XO1GC-p-Q')]",
             'thread_author':   "//div[contains(@class, 'F0XO1GC-rb-b')]",
             'thread_date':     "//div[contains(@class, 'F0XO1GC-rb-g')]/span/@title",
             'thread_posts':    "//div[contains(@class, 'F0XO1GC-rb-d')]",
             'post_author':     "//span[contains(@class, 'F0XO1GC-D-a')]",
             'post_date':       "//span[contains(@class, 'F0XO1GC-nb-Q')]/@title",
             'post_text':       "//div[contains(@class, 'F0XO1GC-nb-P')]/div/div/div/div",
             'post_original':   "//div[contains(@class, 'F0XO1GC-k-c') and contains(@class, 'F0XO1GC-nb-k')]/@id"
             }

def extract_post_count(text):
    try:
        return POST_COUNT_REGEX.search(text).group(1)
    except IndexError:
        return -1
    
             
class ThreadDirectoryScraper:
    def __init__(self, group, after=None, before=None):
        self.group = group
        self.after = after if after is not None else datetime(1900, 1, 1)
        self.before = before if before is not None else datetime.today()
        self.search_url = ''
        self.generate_search_url()
        
        self.scraper_window = None
        self.scraper_window_initialized = False
        self.thread_directory = []
        
    def generate_search_url(self):
        after = urllib.quote_plus(self.after.strftime('%Y/%m/%d'))
        before = urllib.quote_plus(self.before.strftime('%Y/%m/%d'))
        self.search_url = SEARCH_URL.format(group=self.group, after=after, before=before)

    def initialize_window(self, x=1024, y=768):
        self.scraper_window = webdriver.Chrome()
        self.scraper_window.set_window_size(x, y)
        self.scraper_window_initialized = True
        time.sleep(2)
    
    def close_window(self):
        if self.scraper_window_initialized:
            self.scraper_window.close()
            self.scraper_window_initialized = False
    
    def get_visible_threads(self):
        source = self.scraper_window.execute_script(RETURN_HTML)
        page = lxml.html.fromstring(source)
        urls = page.xpath(SELECTORS['thread_url'])
        titles = page.xpath(SELECTORS['thread_title'])
        authors = page.xpath(SELECTORS['thread_author'])
        dates = page.xpath(SELECTORS['thread_date'])
        thread_posts = page.xpath(SELECTORS['thread_posts'])
        threads = []
        
        for t, u, a, d, tp in zip(titles, urls, authors, dates, thread_posts):
            thread = {'group': self.group,
                     'thread_title': t.text,
                     'thread_hashcode': u.rsplit('/', 1)[-1],
                     'thread_author': a.text[3:],
                     'thread_date': d,
                     'thread_posts': extract_post_count(tp.text_content())}
            threads.append(thread)
        
        return threads
    
    def send_key_to_window(self, key, times=1):
        target_element = self.scraper_window.find_element_by_xpath('//html')
        for _ in range(0, times):
            target_element.send_keys(key)
    
    def scroll_window(self):
        thread_count = -1
        new_thread_count = 0
        threads = []

        while new_thread_count != thread_count:
            thread_count = new_thread_count
            threads = self.get_visible_threads()
            if not threads:
                break
            new_thread_count = len(threads)
            self.send_key_to_window(Keys.PAGE_DOWN, times=12)
            time.sleep(3)
        
    def scrape(self, close_window=False):
        if not self.scraper_window_initialized:
            self.initialize_window()
        
        self.scraper_window.get(self.search_url)
        time.sleep(3)
        self.scroll_window()
        self.thread_directory = self.get_visible_threads()
        
        if close_window:
            self.scraper_window.close()
            
    def update_values(self, group=None, after=None, before=None):
        if group:   self.group = group
        if after:   self.after = after
        if before:  self.before = before
        if any([group, after, before]):
            self.generate_search_url()

class ThreadScraper:
    def __init__(self, thread, **kwargs):
        self.thread = thread
        self.thread_url = THREAD_URL.format(group=thread['group'],
                                            hashcode=thread['thread_hashcode'])
        
        self.scraper_window = None
        self.posts = []
        
    def initialize_window(self, x=1024, y=768):
        self.scraper_window = webdriver.Chrome()
        self.scraper_window.set_window_size(x, y)
        self.scraper_window.get(self.thread_url)
        time.sleep(5)
        
    def get_visible_posts(self):
        source = self.scraper_window.execute_script(RETURN_HTML)
        page = lxml.html.fromstring(source)
        
        authors = page.xpath(SELECTORS['post_author'])
        dates = page.xpath(SELECTORS['post_date'])
        texts = page.xpath(SELECTORS['post_text'])
        originals = page.xpath(SELECTORS['post_original'])
        posts = []
        for a, d, t, o in zip(authors, dates, texts, originals):
            post = {'post_author': a,
                    'post_date': d,
                    'post_text': unicode(t.text_content()).encode('utf-8', 'ignore'),
                    'post_original': o}
            post.update(self.thread)
            self.posts.append(post)
        
    def iterate_pages(self):
        i = 1
        while True:
            print 'page {}'.format(i)
            self.get_visible_posts()
            try:
                self.scraper_window.find_element_by_link_text('Next').click()
            except:
                break
            i += 1
        
    def scrape(self):
        self.initialize_window()
        self.iterate_pages()
        self.scraper_window.close()

def save_json(d, filename):
    with open(filename, 'w') as f:
        json.dump(d, f)

def generate_filename(formatter, group, after, before):
    filename = formatter.format(after=after.strftime('%Y%m%d'),
                                before=before.strftime('%Y%m%d'),
                                group=group)
    return filename

def generate_date_ranges(start_date, day_step):
    dates = []
    while start_date <= datetime.today():
        dates.append(start_date)
        start_date += timedelta(days=7)
    date_ranges = zip(dates, dates[1:])
    return date_ranges
    
def sequential_scrape(group, day_step=7):
    date_ranges = generate_date_ranges(datetime(1996, 7, 21), day_step=day_step)
    TDS = ThreadDirectoryScraper(group)
    for after, before in date_ranges:
        TDS.update_values(after=after, before=before)
        fn = generate_filename(THREAD_DIRECTORY_FILENAME, group, after, before)
        if os.path.exists(fn):
            print '{} exists'.format(fn)
            continue
        TDS.scrape()
        save_json(TDS.thread_directory, fn)
        TDS.close_window()
        print '{} saved'.format(fn)
        
# sequential_scrape(group='alt.conspiracy')
all_threads = []
for week_path in glob.glob(os.path.join(CD, 'outputs', '*')):
    all_threads += json.load(open(week_path, 'r'))