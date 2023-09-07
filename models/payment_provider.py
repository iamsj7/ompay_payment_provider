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

from odoo import api, fields, models
import base64


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('ompay', 'OMPay')], ondelete={'ompay': 'set default'})
    ompay_public_key = fields.Char('Publishable Key', required_if_provider='ompay')
    ompay_secret_key = fields.Char('Secret Key', required_if_provider='ompay')
    ompay_merchant_key = fields.Char('Merchant Key', required_if_provider='ompay')

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist OMPay providers for unsupported currencies. """
        providers = super()._get_compatible_providers(*args, currency_id=currency_id, **kwargs)
        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name != 'OMR':
            providers = providers.filtered(
                lambda a: a.code != 'ompay'
            )
        return providers

    def _get_ompay_urls(self):
        """ OMPay URLS """
        if self.state == 'enabled':
            return 'https://api.sandbox.ompay.com'
        return 'https://api.sandbox.ompay.com'

    def _get_ompay_headers(self):
        # Concatenate the public key and secret key with a colon
        credentials = f'{self.ompay_public_key}:{self.ompay_secret_key}'
        # Encode the credentials in Base64
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers = {
            'Content-Type': "application/json",
            'Authorization': f'Basic {encoded_credentials}'
        }
        return headers
