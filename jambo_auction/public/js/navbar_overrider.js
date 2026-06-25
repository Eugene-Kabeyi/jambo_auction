frappe.after_ajax(() => {

    function customizeNavbar() {

        const brand = document.querySelector(".navbar-brand");

        if (!brand) return;

        // Prevent running twice
        if (brand.querySelector(".jambo-brand")) return;

        // Replace everything inside navbar-brand
        brand.innerHTML = `
            <div class="jambo-brand"
                 style="display:flex; align-items:center; gap:10px;">
                
                <img
                    src="/assets/jambo_auction/images/logo.png"
                    style="height:32px; width:auto;"
                >

                <span
                    style="
                        font-weight:700;
                        color:#ffd700;
                        font-size:15px;
                        letter-spacing:1px;
                    ">
                    Jambo Auc Ltd
                </span>

            </div>
        `;
    }

    customizeNavbar();

    // Frappe sometimes rebuilds navbar
    setTimeout(customizeNavbar, 1000);
    setTimeout(customizeNavbar, 3000);
});