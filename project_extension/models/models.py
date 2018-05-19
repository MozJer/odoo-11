# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class Task(models.Model):
    _name = 'project.task'
    priority = fields.Selection(help="Choose your task priority", selection=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ])
