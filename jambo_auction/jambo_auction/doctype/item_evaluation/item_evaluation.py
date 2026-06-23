# Copyright (c) 2026, Eugene Kabeyi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ItemEvaluation(Document):
	def on_submit(self):
		item = frappe.get_doc("Consigner Item", self.consigned_item)

		##### Approve 
		if self.decision == "Approve":
			item.status = "Approved"
			item.save()
		
		##### Reject 
		if self.decision == "Reject":
			item.status = "Rejected"
			item.save()
		