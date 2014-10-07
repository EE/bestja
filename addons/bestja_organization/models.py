# -*- coding: utf-8 -*-

from openerp import models, fields, api

class BankiZywnosci(models.Model):
    _name = 'organization.banki_zywnosci'
    name = fields.Char()

class Organization(models.Model):
    _name = 'organization'
    name = fields.Char(string="Nazwa", required=True)
    krs = fields.Integer(size=10, string="KRS")
    regon = fields.Integer(size=14, string="REGON")
    nip = fields.Integer(size=10, string="NIP")
    #address = fields.Many2one('organization.address', string="Adres")    
    street_address = fields.Char(string="Ulica", required=True)
    city_address = fields.Char(string="Miejscowość", required=True)
    street_number = fields.Char(string="Numer", required=True)
    postal_code = fields.Integer(size=6,string="Kod pocztowy")
    email = fields.Char(string="E-mail", required=True) 
    phone = fields.Integer(size=10, string="Numer Telefonu")
    www = fields.Char(string="WWW")
    fbfanpage = fields.Char(string="Fanpage na FB") 
    bank_zywnosci = fields.Many2one('organization.banki_zywnosci', string="Bank Żywności")

    coordinator = fields.Many2one('res.users', ondelete='set null', 
       string="Koordynator") 

    active = fields.Boolean(default=True)

    storage_street = fields.Char(string="Ulica")
    storage_street_number = fields.Char(string="Numer")
    storage_city_address = fields.Char(string="Miejscowość")
    storage_postal_code = fields.Integer(size=6,string="Kod pocztowy")

    organization_description = fields.Text(string="Opis Organizacji")

    image = fields.Binary("Photo")
    _sql_constraints = [
        ('name_organization_uniq', 'CHECK(1=1)', ''),
    ] 
