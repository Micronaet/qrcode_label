# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import logging
import openerp
import qrcode
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class ZipLabel(orm.Model):
    """ Model name: ZipLabel
    """
        
    _name = 'zip.label'
    _description = 'Zip Label'
    _rec_name = 'code'
    _order = 'code'
    
    def generate_qr_code(self, cr, uid, ids, context=None):
        ''' Generate QR Code for label
        '''
        for label in self.browse(cr, uid, ids, context=context):
            path = '/home/openerp/'
            
            item_id = label.id
            fullname = os.path.join(path, '%s.png' % item_id)
            
            code = label.code
            text_it = label.description_it
            text_en = label.description_en
            qr_mask = 'Zipperr\nCodice: %s\IT: %s\nEN: %s'
            qr_text = qr_mask % (code, text_it, text_en)    
            img = qrcode.make(qr_text)
            img.save(fullname)
        return True
    
    _columns = {
        'code': fields.char(
            'Code', size=64, required=True),
        'description_it': fields.text('Description IT', required=True)
        'description_en': fields.text('Description EN', required=True)
        # qrcode function binary
        }
        
    _defaults = {
        # TODO code automatic
        }    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
