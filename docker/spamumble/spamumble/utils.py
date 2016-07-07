#!/usr/bin/env python

import logging

def log_exceptions(function):
    def new_func(*args, **kwargs):
        try:
            return function(*args, **kwargs) 
        except Exception, e:
            logging.critical(repr(e))
            return None

    new_func.__name__ = function.__name__
    new_func.__doc__ = function.__doc__
    new_func.__dict__.update(function.__dict__)
    return new_func
