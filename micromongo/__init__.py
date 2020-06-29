# -*- coding: utf-8 -*-
'''
    minimongo
    ~~~~~~~~~

    Minimongo is a lightweight, schemaless, Pythonic Object-Oriented
    interface to MongoDB.
'''
from .index import Index
from .collection import Collection
from .model import Model, AttrDict, fields
from .options import configure

__all__ = ('Collection', 'Index', 'Model', 'fields', 'configure', 'AttrDict')


