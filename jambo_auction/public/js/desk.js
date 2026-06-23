frappe.after_ajax(() => {
    setTimeout(() => {

        document.querySelectorAll(
            ".app-title, .navbar-brand-text, .brand-text"
        ).forEach(el => {
            el.innerText = "Jambo Auc. Ltd";
        });

        if (frappe.boot) {
            frappe.boot.sysdefaults.app_name = "Jambo Auc. Ltd";
        }

    }, 300);

});