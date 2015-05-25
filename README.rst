GooDoo
======

GooDoo (codename: BestJa) is an utility for professional management of
volunteers’ work.

There are two websites for which GooDoo has been created, owned by
`Federacja Polskich Banków Żywności <http://bankizywnosci.pl/>`__ and
`Uniwersyteckie Centrum Wolontariatu
<http://wolontariat.uw.edu.pl/>`__. Modules related to these websites
are marked with suffixes ``_fpbz`` and ``_ucw``, respectively.

Modules that are not prefixed with ``bestja_`` may be used outside of
the GooDoo ecosystem.

Installation
------------

Generally GooDoo is based on Odoo 8.0 compatible modules, however
there are some constraints on which version of Odoo can be
used. `Commit 2067a20 <https://github.com/odoo/odoo/commit/2067a20>`__
introduced `a regression <https://github.com/odoo/odoo/issues/5319>`__
in GooDoo, therefore an earlier version of Odoo should be used until
this is fixed.
