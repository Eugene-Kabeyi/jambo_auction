# Copyright (c) 2026, Eugene Kabeyi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AuctionListing(Document):
	 
	# Step 1: Get Item Evaluation linked to this item
	def validate(self):
		evaluation = frappe.get_all(
			"Item Evaluation",
			filters= {
				"consigner_item": self.consigner_item,
				"decision": "Approve"
			},
			fields=["reserved_price"],
			order_by = "creation desc",
			limit = 1
		)

		# Step 2: Ensure evaluation exists
		if not evaluation:
			frappe.throw("No Approved Evaluation on this Item")
		
		reserve_price = evaluation[0].reserved_price

		# Step 3: Set reserve price automatically
		self.reserve_price = reserve_price

        # Step 4: Calculate starting bid
		self.starting_bid = reserve_price + 100

	def before_save(self):
		if self.docstatus == 1:
			frappe.throw("Cannot modify Auction Listing after submission")

	def on_submit(self):
		item = frappe.get_doc("Consigned Items", self.consigned_item)

		item.status = "Scheduled"
		item.save()