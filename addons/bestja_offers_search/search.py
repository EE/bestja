#-*- coding: utf-8 -*-
import os

from whoosh import fields, index, writing, sorting, query
from whoosh.qparser import SimpleParser

from openerp import tools


class OffersSchema(fields.SchemaClass):
    pk = fields.ID(unique=True, stored=True)
    slug = fields.ID(stored=True)
    name = fields.TEXT(stored=True)
    wishes = fields.KEYWORD(commas=True)
    target_group = fields.KEYWORD(commas=True)
    organization = fields.TEXT(stored=True, sortable=True)


class OffersFacets(object):
    # Which fields to facet?
    # schema field name => facet description
    fields_map = {
        'wishes': u'Obszar działania',
        'target_group': u'Adresaci oferty',
    }

    def __init__(self):
        self.facets = sorting.Facets()
        self.schema = OffersSchema()
        for name in self.get_fields():
            # KEYWORD fields may hold multiple values and overlap
            overlap = isinstance(self.schema[name], fields.KEYWORD)
            self.facets.add_field(
                name,
                allow_overlap=overlap,
                maptype=sorting.Count
            )

    def get_fields(self):
        return self.fields_map.keys()

    def get_filter(self, querydict):
        """
        Generates a Whoosh query filter reflecting which facets are currently selected.
        Takes `querydict` - a MultiDict with current HTTP GET params.
        """
        terms = []
        for field in self.get_fields():
            # user-provided values concerning a given field
            values = querydict.getlist('filter_' + field)
            if values:
                subterms = [query.Term(field, val) for val in values]
                terms.append(query.Or(subterms))
        return query.And(terms)

    def facets_with_groups(self, response, querydict):
        """
        Returns a list of facets with grouped values from Whoosh,
        ready to be passed to a template.
        Keyword arguments:
        `reply` - Whoosh response
        `querydict` - a MultiDict with current HTTP GET params.
        """
        facet_list = []
        for field, display_name in self.fields_map.iteritems():
            groups = []
            for value, count in response.groups(field).iteritems():
                groups.append({
                    'value': value,
                    'count': count,
                    'checked': value in querydict.getlist('filter_' + field)
                })
            facet_list.append({
                'field': field,
                'html_name': 'filter_' + field,
                'display_name': display_name,
                'groups': groups,
            })
        return facet_list


class OffersIndex(object):
    INDEX_PREFIX = 'offers'

    def __init__(self, dbname):
        self.dbname = dbname

    def index_name(self):
        return '{prefix}_{db}'.format(
            prefix=self.INDEX_PREFIX,
            db=self.dbname
        )

    def index_dir(self):
        """
        Get / create a directory for storing the index.
        This is in line with where odoo keeps its data
        files - see openerp.tools.config.
        One can change the 'data_dir' value by running odoo
        server with the --data-dir option.
        """
        d = os.path.join(tools.config['data_dir'], 'whoosh')
        if not os.path.exists(d):
            os.makedirs(d, 0700)
        else:
            os.chmod(d, 0700)
        return d

    def create_index(self):
        return index.create_in(self.index_dir(), schema=OffersSchema(), indexname=self.index_name())

    def get_index(self):
        dirname = self.index_dir()
        if not index.exists_in(dirname, indexname=self.index_name()):
            return self.create_index()
        return index.open_dir(dirname, indexname=self.index_name())

    def get_writer(self):
        return writing.AsyncWriter(self.get_index())

    def get_parser(self):
        return SimpleParser('name', schema=OffersSchema())
