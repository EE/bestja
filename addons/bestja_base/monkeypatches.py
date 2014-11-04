# encoding: utf-8

from __future__ import unicode_literals

import openerp.modules.loading
from openerp.modules.loading import load_module_graph as old_load_module_graph


# We skip loading demo data for projects because it conflicts with model
# changes in bestja_project module.
def load_module_graph(cr, graph, *args, **kwargs):
    for package in graph:
        if package.name == 'project':
            if hasattr(package, 'demo'):
                del package.demo
            package.dbdemo = False
    return old_load_module_graph(cr, graph, *args, **kwargs)
openerp.modules.loading.load_module_graph = load_module_graph
