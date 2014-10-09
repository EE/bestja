import os

from whoosh import fields, index, writing
from whoosh.qparser import SimpleParser

from openerp import tools


class OfferSchema(fields.SchemaClass):
    pk = fields.ID(stored=True)
    name = fields.TEXT(stored=True)
    wishes = fields.KEYWORD(commas=True)
    target_group = fields.KEYWORD(commas=True)
    organization = fields.TEXT(stored=True, sortable=True)
    project = fields.STORED()


def index_dir():
    """
    Get / create a directory for storing the index.
    This is in line with where odoo keeps its data
    files - see opernerp.tools.config.
    One can change the 'data_dir' value by running odoo
    server with the --data-dir option.
    """
    d = os.path.join(tools.config['data_dir'], 'whoosh')
    if not os.path.exists(d):
        os.makedirs(d, 0700)
    else:
        os.chmod(d, 0700)
    return d


def get_index():
    dirname = index_dir()
    indexname = 'offers'
    if not index.exists_in(dirname, indexname=indexname):
        return index.create_in(dirname, schema=OfferSchema(), indexname=indexname)
    return index.open_dir(dirname, indexname=indexname)


def get_writer():
    return writing.AsyncWriter(get_index())


def get_parser():
    return SimpleParser('name', schema=OfferSchema())
