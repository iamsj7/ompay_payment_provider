# ******************************************************************************
# Copyright (c) [2023] [Shaik Jaleel]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# For more information, please refer to https://github.com/iamsj7/ompay_payment_provider.
# ******************************************************************************

import logging
import json
import requests

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ompay_customer_id = fields.Char('OMPay Customer ID')
    ompay_provider = fields.Many2one('payment.provider', 'OMPay Provider')

    def _create_ompay_customer(self, provider):
        if not self.ompay_customer_id:
            url = provider._get_ompay_urls()
            headers = provider._get_ompay_headers()

            payload = {
                "client_customer_id": self.email
            }

            res = requests.request("POST", url + '/api/v1/customers', data=json.dumps(payload), headers=headers)
            response = res.json()
            if 'success' not in response.keys():
                _logger.info(_("OMPay Error response: %s") % response)
                raise ValidationError(_("OMPay is having some issues, contact us for the support!"))
            elif not response.get('success'):
                _logger.info(_("OMPay Error response: %s") % response)
                raise ValidationError(_("OMPay is having some issues, contact us for the support!"))
            self.sudo().write({'ompay_customer_id': response['data']['id'], 'ompay_provider': provider.id})
        return self.ompay_customer_id

    def unlink(self):
        try:
            if self.ompay_customer_id and self.ompay_provider:
                url = self.ompay_provider._get_ompay_urls()
                headers = self.ompay_provider._get_ompay_headers()

                res = requests.request("DELETE", url + '/api/v1/customers/%s' % self.ompay_customer_id, headers=headers)

                response = res.json()
                if 'success' not in response.keys():
                    _logger.info(_("OMPay Error response: %s") % response)
                elif not response.get('success'):
                    _logger.info(_("Can not able to delete the customer from ompay database, error response: %s") % response)
        except:
            pass
        return super(ResPartner).unlink
