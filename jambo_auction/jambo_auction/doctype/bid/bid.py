# Copyright (c) 2026, Eugene Kabeyi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Bid(Document):
    def validate(self):
        self.validate_kyc()
        self.validate_bid_amount()
        self.validate_bidder_status()

    def validate_kyc(self):

        # Get system settings
        settings = frappe.get_single("KYC Settings")

        # Skip validation if KYC is not required
        if not settings.require_kyc_for_bidding:
            return

        # Get bidder record
        bidder = frappe.get_doc("Bidders", self.bidder)

        # Verify KYC status
        if bidder.kyc_status != "Verified":
            frappe.throw("You must complete KYC verification before placing bids.")
            
    def validate_bid_amount(self):
        if self.bid_amount <= 0:
            frappe.throw("Bid amount must be greater than zero.")
            
    def validate_bidder_status(self):
        bidder = frappe.get_doc("Bidders", self.bidder)
        if bidder.status != "Active":
            frappe.throw(f"Bidder account is {bidder.status}. Bidding is not allowed.")
