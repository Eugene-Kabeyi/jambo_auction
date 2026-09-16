// Copyright (c) 2026, Eugene Kabeyi and contributors
// For license information, please see license.txt

frappe.ui.form.on("KYC Verification", {
    refresh(frm) {
        // Only show button after the document row exists in the DB
        if (!frm.is_new()) {

            frm.add_custom_button("Verify KYC", function () {
                
                // FIXED: Direct API invocation removes dependency on standard frm.save() promise chains
                frappe.call({
                    method: "jambo_auction.api.kyc_api.process_kyc",
                    args: {
                        "bidder": frm.doc.bidder,
                        "document_type": frm.doc.document_type || "National ID",
                        "front_image": frm.doc.front_image,
                        "back_image": frm.doc.back_image || null
                    },
                    freeze: true,
                    freeze_message: "Processing local Tesseract OCR... Please wait",
                    
                    callback: function (r) {
                        if (r.message) {
                            frappe.msgprint({
                                title: "KYC Result Summary",
                                message: "<b>Status:</b> " + r.message.status + 
                                         "<br><b>Confidence:</b> " + r.message.confidence +
                                         "<br><b>Extracted ID:</b> " + (r.message.id_number || "Not Found"),
                                indicator: r.message.status === "Verified" ? "green" : "red"
                            });
                            
                            // FIXED: Forcefully wipe local UI cache variables to allow changes to display
                            frappe.model.clear_doc(frm.doc.doctype, frm.doc.name);
                            
                            // Pull a fresh layout dataset directly out of the database
                            frappe.model.with_doc(frm.doc.doctype, frm.doc.name, function() {
                                frm.refresh();
                            });
                        }
                    }
                });

            }).addClass("btn-primary");
        }
    }
});
