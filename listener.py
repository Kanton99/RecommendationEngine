import logging
import re
import sys
import time
import recommender
import threading
from parser import parser,file_parser

from watchdog.events import *
from watchdog.events import FileCreatedEvent
from watchdog.observers import Observer

class Listener(threading.Thread):

    def __init__(self,thread_ID,name,Recommender):
        threading.Thread.__init__(self)
        self.thread_ID = thread_ID
        self.name = name
        self.Recommender = Recommender

    def run(self):
        print("Starting {} watchdog".format(self.name))
        directory_listener(self.Recommender)

        
def directory_listener(Recommender=None,dir=".", ):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = dir
    reg = "(.*)(interactions_users_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_([0-9]*)[0-9].json$)"
    event_handler = RegexMatchingEventHandler(regexes=[reg])

    def on_created(event):
        print("file {} created".format(event.src_path))
    def on_deleted(event):
        print("file {} deleted".format(event.src_path))
    def on_moved(event):
        print("file {} moved".format(event.src_path))
    def on_modified(event):
        print("file {} modified".format(event.src_path))
        rData = file_parser(event.src_path)
        try:
            Recommender.update(rData)
        except:
            print("recommender error",sys.exc_info()[0])

    event_handler.on_created = on_created
    event_handler.on_moved = on_moved
    event_handler.on_deleted = on_deleted
    event_handler.on_modified = on_modified
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    
