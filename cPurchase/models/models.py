# -*- coding:utf-8 -*-
# ---------------------------------------------------------------------
# 
# ---------------------------------------------------------------------
# Copyright (c) 2017 BDC International Develop Team and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 11-04-19

from openerp import models, fields, api
from openerp.tools.translate import _
from odoo import exceptions

class PurchaseOrder(models.Model):
    """
    Purchase Order model customization.
    
    """
    _inherit = 'purchase.order'

    user_department_id = fields.Many2one('hr.department', store=True,
                                         compute='_compute_user_department')
    state = fields.Selection([('draft', 'RFQ'),
                              ('sent', 'RFQ Sent'),
                              ('to approve', 'To Approve'),
                              ('purchase', 'Purchase Order'),
                              ('Approved', 'Approved'),
                              ('done', 'Locked'),
                              ('cancel', 'Cancelled')],
                             string='Status', readonly=True,
                             index=True, copy=False,
                             default='draft', track_visibility='onchange')

    @api.multi
    def action_view_invoice(self):
        '''Is needed redefine for avoid that the user can create a bill
        without a department manager approved.

        '''
        if self.state == 'Approved':
            return super(PurchaseOrder,self).action_view_invoice()
        else:
            raise exceptions.ValidationError(_('"Error"\
            Please aprove the purchase first..'))

    @api.multi
    def aprove_purchase(self):
        ''' Confirm the purchase.
        Also check if the logged user have the needed access for confirm a
        purchase order and raise an exception if not.

        '''
        # groups_name = ['Technical Features']
        groups_name = []
        if self.user_department_id:
            groups_name.append(
                self.user_department_id.name + '_Purchases_Manager')
            groups_name.append(
                self.user_department_id.name + '_Admin_Purchases')
        manager_groups = self.env['res.groups'].search([
            ('name','in', groups_name)
        ])
        flag = False
        for group in manager_groups:
            if self.env.user.id in group.users.ids:
                self.write({'state': 'Approved'})
                flag = True
        if not flag:
            raise exceptions.ValidationError(_('"Error"\
            You have no access to confirm a Purchase, please contact with\
            the department manager.'))
        else:
            self.build_invoice()

    def build_invoice(self):
        ''''This method will build an invoice using the purchase fields and
        related with the PO.

        '''
        AccountInvoice = self.env['account.invoice']
        AccountJournal = self.env['account.journal']
        purchaseJournal = AccountJournal.search([('type','=','purchase')])
        assert purchaseJournal,'Please create a purchase type journal.'
        p_expense_acc = self.order_line.product_id.property_account_expense_id
        invoice = AccountInvoice.create({
            'partner_id' : self.partner_id.id,
            'currency_id' : self.company_id.currency_id.id,
            'journal_id' : purchaseJournal.id,
            'company_id' : self.company_id.id,
            'purchase_id' : self.id,
            'origin' : self.name,
            'state' : 'draft',
            'type' : 'in_invoice',
            'user_id' : self.user_id.id,
            'create_date' : self.create_date,
            'write_uid' : self.write_uid.id,
            'write_date' : self.write_date,
            'invoice_line_ids' :
            [
            (0, 0, {
                'name': self.name + ':' +self.product_id.name,
                'origin': self.name,
                'uom_id': self.order_line.product_uom.id,
                'product_id': self.order_line.product_id.id,
                'account_id': p_expense_acc.id,
                'price_unit': self.order_line.price_unit,
                'price_subtotal': self.order_line.price_subtotal,
                'price_total': self.order_line.price_total,
                'quantity': self.order_line.product_qty,
                'company_id': self.company_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.company_id.currency_id.id,
                'create_uid': self.create_uid.id,
                'create_date': self.create_date,
                'write_uid': self.write_uid.id,
                'write_date': self.write_date,
                'purchase_line_id': self.order_line.id})
            ]
        })
        invoice.action_invoice_open()
        return {
            'name': 'Test',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form, search',
            'res_model': 'account.invoice',
            'target': 'current',
            'res_id': invoice.id,
            'context': { }
        }

    @api.multi
    @api.depends('partner_id')
    def _compute_user_department(self):
        ''' Define if the logged user have an assigned department and store
        it in the purchase order for filter later using the created user
        rules.

        '''
        for record in self:
            if record.user_id.employee_ids.department_id:
                record.user_department_id = record.user_id.employee_ids.department_id.id


class HrDeparment(models.Model):
    """
    Hr Department Model customization.
    TODO: DOCUMENT
    
    """
    _inherit = 'hr.department'

    @api.model
    def create(self, vals):
        ''' Create the category, groups related with this new 
        department so the users could have two roles; user or manager
        and each one of this have diferents access level.

        '''
        IrModuleCat = self.env['ir.module.category']
        ResGroups = self.env['res.groups']
        IrRule = self.env['ir.rule']
        dptoCateg = IrModuleCat.sudo().create({
            'name' : vals.get('name') + " Deparment",
            'description' : 'Custom Purchase {dptoName}'.format(
                dptoName=vals.get('name', '')),
            'sequence' : 1
        })
        purchase_model_id = self.env['ir.model'].search(
            [('name', '=', 'Purchase Order')])        
        group_user = ResGroups.create({
            'name': '{dptoName}_Purchases_User'.format(
                dptoName=vals.get('name')),
            'category_id' : dptoCateg.id,
            # 'implied_ids': ResGroups.search([('name', '=', 'User')])
        })
        user_domain = "[('create_uid','=',user.id)]"
        userRule = IrRule.create({
            'name': 'Custom_Purchase_User_Rule_{dptoName}'.format(
                dptoName=vals.get('name')),
            'model_id': purchase_model_id.id,
            'groups': group_user,
            'domain_force': user_domain
        })
        userRule.groups = group_user        
        # ******************************************************************        
        group_manager = ResGroups.create({
            'name': '{dptoName}_Purchases_Manager'.format(
                dptoName=vals.get('name')),
            'category_id' : dptoCateg.id,
            # 'implied_ids': ResGroups.search([('name', '=', 'User')])
        })
        manager_domain = "['|', ('create_uid', '=', user.id),\
        ('user_department_id.member_ids.user_id', 'in', [user.id])]"
        managerRule = IrRule.create({
            'name': 'Custom_Purchase_Manager_Rule_{dptoName}'.format(
                dptoName=vals.get('name')),
            'model_id': purchase_model_id.id,
            'groups': group_manager,
            'domain_force': manager_domain
        })
        managerRule.groups = group_manager
        # ******************************************************************
        group_admin = ResGroups.create({
            'name': '{dptoName}_Admin_Purchases'.format(
                dptoName=vals.get('name')),
            'category_id' : dptoCateg.id,
        })
        managerRule = IrRule.create({
            'name': 'Custom_Purchases_Admin_Rule_{dptoName}'.format(
                dptoName=vals.get('name')),
            'model_id': purchase_model_id.id,
            'groups': group_admin,
            'domain_force': "[(1,'=',1)]"
        })
        managerRule.groups = group_admin
        return super(HrDeparment,self).create(vals)
