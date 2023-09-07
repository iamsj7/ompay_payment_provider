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

{
    'name': 'OMPay Payment Provider',
    'category': 'Accounting/Payment Providers',
    'version': '16.0.1.2',
    'license': 'OPL-1',
    'author': 'Shaik Jaleel',
    'website': 'https://shaikjaleel.in',
    'depends': ['payment'],
    'data': [
        'views/payment_ompay_templates.xml',
        'views/payment_views.xml',
        'data/payment_provider_data.xml',
    ],
    'images': [
        'static/description/banner.gif',
    ],
    'application': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'description': """OMPay Payment Provider""",
    'price': 149,
    'currency': 'usd',
    'summary': '''
        Payment Provider: OMPay Payment Gateway
        Online Payment
        E-commerce Payment
        Invoice Payment
        Debit Card Payment
        Credit Card Payment
        Omani rial
        OMR
        Oman Payment
    '''
}
