# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class Asset(models.Model):
    _name = 'asset_management.asset'
    name = fields.Char(string="Asset Number", index=True,readonly=True)
    description = fields.Text("Description")
    #units = fields.Integer("Units")
    ownership_type = fields.Selection(selection=[('owned', 'Owned')
        , ('leased', 'Leased')])
    is_new = fields.Selection(selection=[('new', 'New')
        , ('used', 'Used')])
    is_in_physical_inventory = fields.Boolean()
    in_use_flag = fields.Boolean(required=True)
    parent_asset = fields.Many2one('asset_management.asset', on_delete='cascade')
    item_id = fields.Many2one('product.product', on_delete='set_null')
    category_id = fields.Many2one('asset_management.category', required=True)
    book_assets_id = fields.One2many(comodel_name="asset_management.book_assets", inverse_name="asset_id", string="Book")
    depreciation_id = fields.One2many(comodel_name="asset_management.depreciation", inverse_name="asset_id", string="depreciation")
    asset_serial_number = fields.Char(string ='Serial Number' )
    asset_tag_number = fields.Many2many('asset_management.tag')
    assignment_id = fields.One2many('asset_management.assignment','asset_id')
    _sql_constraints=[
        ('asset_serial_number','UNIQUE(asset_serial_number)','Serial Number already exists!')
    ]
    asset_with_category=fields.Boolean(related='category_id.asset_with_category')

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('asset_management.asset.Asset')
    #     record=super(Asset, self).create(values)
    #     self.env['asset_management.transaction'].create({
    #          'asset_id': record.id,
    #          'trx_type': 'addition',
    #          'trx_date': datetime.today(),
    #          })
        return super(Asset, self).create(values)

    @api.multi
    def write(self, values):
        old_value=self.category_id
        super(Asset, self).write(values)
        if 'category_id' in values:
            if self.category_id != old_value:
                for record in self:
                    self.env['asset_management.transaction'].create({
                         'asset_id': record.id,
                         'trx_type': 're_class',
                         'trx_date': datetime.today(),
                         'category_id':self.category_id.id,
                         })
                return record

    @api.onchange('category_id')
    def onchange_method(self):
        if self.category_id:
                self.asset_with_category = True

    # @api.onchange('category_id')
    # def  _onchange_category_id(self):
    #     old_value=self._origin.category_id
    #     if self.category_id:
    #          record_exist = self.env['asset_management.transaction'].search([('asset_id','=',self._context.get('id'))],limit=1)
    #          if record_exist:
    #             if self.category_id != old_value:
    #                  self.env['asset_management.transaction'].create({
    #                         'asset_id':self.id,
    #                         'trx_type': 're_class',
    #                         'trx_date': datetime.today(),
    #                       #'category_id' :self.category_id
    #                 })
    #          else:
    #             self.env['asset_management.transaction'].create({
    #                 'asset_id':self.id,
    #                 'trx_type': 'addition',
    #                 'trx_date': datetime.today(),
    #               #  'category_id':self._context.get('category_id')
    #             })


class Category(models.Model):
    _name = 'asset_management.category'
    name = fields.Char(string='Category Name',index=True)
    description = fields.Text()
    ownership_type = fields.Selection(selection=[('owned', 'Owned')
        , ('leased', 'Leased')])
    is_in_physical_inventory = fields.Boolean()
    category_books_id=fields.One2many('asset_management.category_books','category_id',on_delete='cascade')
    depreciation_method = fields.Selection([('linear','Linear'),('degressive','Degressive')],
    default='linear')
    asset_with_category=fields.Boolean()


class Book(models.Model):
    _name = 'asset_management.book'
    name = fields.Char(index=True)
    description = fields.Text()
    proceeds_of_sale_gain_account = fields.Many2one('account.account', on_delete='set_null')
    proceeds_of_sale_loss_account = fields.Many2one('account.account', on_delete='set_null')
    proceeds_of_loss_clearing_account = fields.Many2one('account.account', on_delete='set_null')
    cost_of_removal_gain_account = fields.Many2one('account.account', on_delete='set_null')
    cost_of_removal_loss_account = fields.Many2one('account.account', on_delete='set_null')
    cost_of_removal_clearing_account = fields.Many2one('account.account', on_delete='set_null')
    net_book_value_retired_gain_account = fields.Many2one('account.account', on_delete='set_null')
    net_book_value_retired_loss_account = fields.Many2one('account.account', on_delete='set_null')
    reval_reserve_retire_gain_account = fields.Many2one('account.account', on_delete='set_null')
    reval_reserve_retire_loss_account = fields.Many2one('account.account', on_delete='set_null')
    deferred_depreciation_reserve_account = fields.Many2one('account.account', on_delete='set_null')
    depreciation_adjustment_account = fields.Many2one('account.account', on_delete='set_null')
    book_with_cate = fields.Boolean()

    # @api.model
    # def create(self, values):
    #     values['name']=self.env['ir.sequence'].next_by_code('asset_management.book.Book')
    #     return super(Book, self).create(values)



class Book_Assets (models.Model):
    _name='asset_management.book_assets'
    name=fields.Char( string="Book Asset Number",index=True)
    book_id = fields.Many2one('asset_management.book',required= True,on_delete= 'cascade')
    asset_id = fields.Many2one('asset_management.asset',required= True,on_delete = 'cascade')
    current_cost = fields.Float(string = "Current Cost")
    salvage_value = fields.Float()
    depreciation_method = fields.Selection(
        [('liner','Liner'),
         ('degressive','Degressive')
         ]
    )
    life_months = fields.Integer()
    original_cost = fields.Float()
    salvage_value_type = fields.Selection(
        [('first','First Type')]
    )
    date_in_service = fields.Date(string = 'Date In Service')
    prorate_date= fields.Date(string = 'Prorate Date')
    prorate_convenction = fields.Selection(
        [('first','First Convention')]
    )
    depreciated_flag = fields.Boolean(string='Depreciated',default =True)

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('asset_management.book_assets.Book_Assets')
        record = super(Book_Assets, self).create(values)
        self.env['asset_management.transaction'].create({
                 'asset_id': record.asset_id.id,
                 'book_id':record.book_id.id,
                 'category_id': self.asset_id.category_id.id,
                 'trx_type': 'addition',
                 'trx_date': datetime.today(),
                 })
        return record


    @api.onchange('current_cost')
    def _onchange_current_cost(self):
        if self.current_cost:
            self.env['asset_management.transaction'].create({
                'asset_id': self.asset_id.id,
                'book_id': self.book_id.id,
                'category_id':self.asset_id.category_id.id,
                'trx_type': 'cost_adjustment',
                'trx_date': datetime.today(),
            })


class Assignment(models.Model):
    _name = 'asset_management.assignment'
    name = fields.Char(string="Assignment",readonly='True',index=True)
    book_assets_id = fields.Many2one('asset_management.book_assets',on_delete = 'cascade')
    book_id = fields.Many2one("asset_management.book", string="Book",on_delete = 'cascade' )
    asset_id = fields.Many2one("asset_management.asset", string="Asset", on_delete='cascade')
    expence_Acc_ID = fields.Many2one('account.account', on_delete='set_null')
    responsible_id = fields.Many2one('hr.employee', on_delete='set_null')
    location_id = fields.Many2one('asset_management.location')
    is_not_used = fields.Boolean( defult = False )
    end_use_date = fields.Date()
    transfer_date = fields.Date()
    comments = fields.Text()
    # units = fields.Integer()
    # units_to_assign= fields.Integer(string = "Units to Assign ,compute = '_get_units_to_assign')
    # @api.depends('responsible_id')
    # def _get_default_location(self):
    #    for record in self:
    #        record.location_id=record.responsible_id.work_location
    # @api.depends('units')
    # def _get_units_to_assign(self):
    #     for record in self:
    #       record.units_to_assign= record.book_assets_id.asset_id.units-record.units

    @api.model
    def create(self, values):
        values['name']=self.env['ir.sequence'].next_by_code('asset_management.assignment.Assignment')
        return super(Assignment, self).create(values)

    @api.onchange('responsible_id','location_id')
    def _onchange_assignment(self):
        if self.responsible_id or self.location_id:
            self.env['asset_management.transaction'].create({
                'asset_id':self.asset_id.id,
                'category_id':self.asset_id.category_id.id,
                'trx_type': 'transfer',
                'trx_date': datetime.today()
                    })

    @api.onchange('end_use_date')
    def onchange_method(self):
       if self.end_use_date :
           self.is_not_used = True

    # @api.onchange('book_id')
    # def onchange_method(self):
    #     if self.book_id :
    #         x=[]
    #         result = self.env['asset_management.book_assets'].search([('book_id', '=', self.book_id.id)])
    #         for r in result:
    #             x+=[r.asset_id.id]
    #
    #         # result1=self.env['asset_management.asset'].search([('id','=',result.asset_id.id)])
    #         # res=result1.mapped('id')
    #         return {'domain':{'asset_id':[('id', 'in',x)]
    #                           }}


class Source_Line(models.Model):
    _name = 'asset_management.source_line'
    name = fields.Char(string="Source Line Number",readonly=True,index=True)
    asset_id = fields.Many2one('asset_management.asset',on_delete = 'cascade')
    source_type = fields.Selection(
        [
            ('invoice','Invoice'),
            ('po','Purchase Order')
        ]
    )
    #source_id = fields.Char(sting='Source')
    invoice_id = fields.Many2one(comodel_name="account.invoice", string="invoice")
    po_id = fields.Many2one(comodel_name="purchase.order", string="purchase order")
    #po_line_id=fields.Many2one(comodel_name="purchase.order.line", string="purchase order",compute="_get_po_line")
    amount = fields.Float('Amount')
    description = fields.Text()

    @api.model
    def create(self, values):
        values['name']=self.env['ir.sequence'].next_by_code('asset_management.source_line.Source_Line')
        return super(Source_Line, self).create(values)





class Retirement (models.Model):
    _name = 'asset_management.retirement'
    name=fields.Char(string="Retirement Number",readonly=True,index=True)
    book_assets_id = fields.Many2one('asset_management.book_assets',on_delete = 'cascade')
    book_id=fields.Many2one('asset_management.book',required = True,on_delete = 'cascade')
    asset_id = fields.Many2one('asset_management.asset', required=True, on_delete='cascade')
    retire_date = fields.Date(string = 'Retire Date')
    comments = fields.Text(string = "Comments")
    current_cost = fields.Float(string= "Current Cost")
    units_retired = fields.Integer(string ='Units Retired')
    current_units = fields.Integer(string="Units to Assign"
                                      , compute='_get_current_units')
    gain_loss_amount=fields.Float()
    proceeds_of_sale = fields.Float()
    cost_of_removal= fields.Float()
   # sold_to=fields.Char()
    partner_id = fields.Many2one(comodel_name="res.partner", string="Sold To")
    check_invoice= fields.Char()

    @api.model
    def _get_current_units(self):
        return self.book_assets_id.asset_id.units - self.units_retired

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('asset_management.retirement.Retirement')
        return super(Retirement,self).create(values)


class Category_Books(models.Model):
    _name= 'asset_management.category_books'
    name = fields.Char(string="Category Books Num",index=True)
    category_id = fields.Many2one('asset_management.category',required=True
                                        ,on_delete='cascade',string='Category')
    book_id = fields.Many2one('asset_management.book',required = True,on_delete='cascade',string='Book Num')
    asset_cost_account = fields.Many2one('account.account',on_delete='set_null')
    asset_clearing_account = fields.Many2one('account.account', on_delete='set_null')
    depreciation_expense_account = fields.Many2one('account.account', on_delete='set_null')
    accumulated_expense_account = fields.Many2one('account.account', on_delete='set_null')
    bonus_expense_account = fields.Many2one('account.account', on_delete='set_null')
    bonus_reserve_account = fields.Many2one('account.account', on_delete='set_null')
    cip_cost_account =fields.Many2one('account.account', on_delete='set_null')
    cip_clearing_account = fields.Many2one('account.account', on_delete='set_null')
    book_with_cate=fields.Boolean(related='book_id.book_with_cate')
    test_field=fields.Boolean()
    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('asset_management.category_books.Category_Books')
        return super(Category_Books, self).create(values)

    @api.onchange('book_id')
    def onchange_method(self):
        if self.book_id:
            # book_search=self.env['asset_management.book'].search([('id','=',self.book_id.id)])[0]
            # if book_search:
                self.book_with_cate = True


class Transaction (models.Model):
    _name = 'asset_management.transaction'
    name =fields.Char(string="Transaction Number",readonly=True,index=True)
   # book_assets_id= fields.Many2one('asset_management.book_assets',required =True,on_delte = 'cascade')
    asset_id=fields.Many2one('asset_management.asset',on_delete='cascade',string="Asset")
    book_id=fields.Many2one('asset_management.book',on_delete='cascade',string="Book")
    category_id = fields.Many2one("asset_management.category", string="Category",on_delete='cascade')
    trx_type = fields.Selection(
        [
		     ('addition','Addition'),
			('re_class','Re_Class'),
            ('transfer','Transfer'),
            ('cost_adjustment','Cost Adjustment')
        ]
    )
    trx_date = fields.Date('Transaction Date')
    cost = fields.Float('Cost')
    trx_details = fields.Text('Trx Details')
    period = fields.Selection(
        [('1','JAN'),
         ('2','FEB'),
         ('3','MAR')]
    )

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('asset_management.transaction.Transaction')
        return super(Transaction, self).create(vals)

    # @api.depends('asset_id')
    # def _get_category_id(self):
    #     for record in self:
    #         record.category_id = record.asset_id.category_id.id
    #         return record.category_id


    # @api.depends('asset_id')
    # def _get_book_id(self):
    #         asset_in_book= self.env['asset_management.book_assets'].search([('asset_id','=',self.asset_id.id)])
    #         self.book_id=asset_in_book.book_id


class Depreciation(models.Model):
    _name = 'asset_management.depreciation'
    name = fields.Char(string="Depreciation Number",readonly=True,index=True)
    book_assets_id = fields.Many2one('asset_management.book_assets', on_delte='cascade')
    asset_id = fields.Many2one('asset_management.asset', required=True, on_delte='cascade')
    book_id = fields.Many2one('asset_management.book', required=True, on_delte='cascade')
    period = fields.Selection(
        [('1', 'JAN'),
         ('2', 'FEB'),
         ('3', 'MAR')]
    )
    depreciation_amount = fields.Float()
    adjustment_amount = fields.Float()

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('asset_management.depreciation.Depreciation')
        return super(Depreciation,self).create(values)



class AssetTag(models.Model):
    _name = 'asset_management.tag'
    name = fields.Char()


class AssetLocation(models.Model):
    _name = 'asset_management.location'
    name = fields.Char()