import uuid
import threading
import os
from os import path


HOME=path.abspath(path.join(path.dirname(path.abspath(__file__)), '..', '..'))

def to_uuid(string):
    "Convert given string to UUID, return None if not possible"
    try:
        return uuid.UUID(string)
    except ValueError:
        return None

def truncate(string, length, suffix="..."):
    "Truncate string to a given length, preserving last word"
    if len(string) <= length:
        return string
    else:
        return string[:length].rsplit(' ', 1)[0] + suffix

def deproxy(o):
    "Returns a real current object if an object is a Flask proxy"
    if getattr(o, "_get_current_object", None):
        o = o._get_current_object()
    return o

class SafeSet():

    def __init__(self):
        self.data = set()
        self.lock = threading.Lock()

    def add(self, element):
        with self.lock:
            if element in self.data:
                raise Exception("Element already exists")
            self.data.add(element)

    def remove(self, element):
        with self.lock:
            self.data.remove(element)

    def contains(self, element):
        with self.lock:
            return element in self.data

def safe_get(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def env_dict(env_list):
    return dict(filter(lambda e: len(e) == 2, map(lambda e: e.split("=", 1), env_list)))

