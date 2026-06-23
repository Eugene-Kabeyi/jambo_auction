// Copyright (c) 2026, Eugene Kabeyi and contributors
// For license information, please see license.txt
frappe.ui.form.on("Consigned Items", {
    onload(frm) {
        // Appends the query during initial form rendering
        set_category_filter(frm);
    },
    refresh(frm) {
        // Double-checks that the filter is active on a doc refresh
        set_category_filter(frm);
    }
});

function set_category_filter(frm) {
    frm.set_query("category", () => {
        return {
            filters: {
                "selectable": 1
            }
        };
    });
}