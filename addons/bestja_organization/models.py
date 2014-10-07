# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Address (models.Model):
    _name="organization.address"

class Organization(models.Model):
    _name = 'organization'
    name = fields.Char(string="Nazwa", required=True)
    krs = fields.Integer(size=10, string="KRS")
    regon = fields.Integer(size=14, string="REGON")
    nip = fields.Integer(size=10, string="NIP")
    #address = fields.Many2one('organization.address', string="Adres")    
    street_address = fields.Char(string="Ulica", required=True)
    city_address = fields.Char(string="Miasto", required=True)
    street_number = fields.Integer(string="Numer domu", required=True)
    flat_number = fields.Integer(string="Numer lokalu")
    postal_code = fields.Integer(size=6,string="Kod pocztowy")
    email = fields.Char(string="E-mail", required=True) 
    phone = fields.Integer(size=10, string="Numer Telefonu")
    coordinator = fields.Many2one('res.users', ondelete='set null', 
       string="Koordynator") 

    _sql_constraints = [
        ('name_organization_uniq', 'CHECK(1=1)', ''),
    ] 
