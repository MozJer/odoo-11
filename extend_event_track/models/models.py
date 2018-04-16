# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import UserError, AccessError, ValidationError
class TrackAttendee(models.Model):
        _name='track.attendee'
        _inherit='event.registration'
        track_id = fields.Many2one(comodel_name="event.track")


class EventTrack(models.Model):
    _inherit='event.track'
    attendee_id = fields.One2many(comodel_name="track.attendee", inverse_name="track_id")

    @api.multi
    def attendee_name(self):
        partner_ids = self.env['event.registration'].search([('event_id', '=', self.event_id.id)])
        if not partner_ids:
            raise UserError(_('no partner _ids!'))
        else:
            for attendee in partner_ids:
                values = {
                    'partner_id': attendee.partner_id.id,
                    'name': attendee.name,
                    'email': attendee.email,
                    'phone': attendee.phone,
                    'event_id': self.event_id.id,
                    'state': attendee.state,
                }
                self.write({'attendee_id': [(0, False, values)]})
        return True








    # @api.model
    # def create(self, values):
    #     partner_ids = self.env['event.registration'].search([('event_id', '=', self.event_id)])
    #     super(EventTrack, self).create(values)
    #     for x in partner_ids:
    #         record = self.env['track.attendee'].create({
    #             'partner_id': x.partner_id,
    #             'name': x.name,
    #             'email': x.email,
    #             'phone': x.phone,
    #             'event_id': self.event_id,
    #             'state': x.state
    #         })
    #         return record







