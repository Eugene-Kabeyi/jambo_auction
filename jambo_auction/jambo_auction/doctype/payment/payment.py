# Copyright (c) 2026, Eugene Kabeyi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Payment(Document):

    def validate(self):
        self.fetch_rates()

    def fetch_rates(self):

        settings = frappe.get_single("Auction Settings")

        self.commission_rate = settings.default_commission_rate
        self.tax_rate = settings.default_tax_rate
        self.buyer_premium_rate = settings.default_buyer_premium_rate