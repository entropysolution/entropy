# -*- coding: utf-8 -*-
'''
    minimongo
    ~~~~~~~~~

    Minimongo is a lightweight, schemaless, Pythonic Object-Oriented
    interface to MongoDB.
'''
from .index import Index
from .collection import Collection
from .model import Model, AttrDict, fields, validate, ExtSchema
from .options import configure

__all__ = ('Collection', 'Index', 'Model', 'fields', 'validate', 'configure', 'AttrDict', 'ExtSchema')


