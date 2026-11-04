// Assignment Group Portal - Client Interactivity

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Bootstrap Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl));

    // 2. Dark/Light Theme Switcher
    const themeToggleBtn = document.getElementById("theme-toggle-btn");
    const storedTheme = localStorage.getItem("portal-theme") || "light";
    document.documentElement.setAttribute("data-bs-theme", storedTheme);
    updateThemeIcon(storedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-bs-theme");
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-bs-theme", newTheme);
            localStorage.setItem("portal-theme", newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        const icon = document.getElementById("theme-icon");
        if (icon) {
            if (theme === "dark") {
                icon.className = "bi bi-sun-fill text-warning";
            } else {
                icon.className = "bi bi-moon-stars-fill text-secondary";
            }
        }
    }

    // 3. Auto-dismiss flash alerts after 5 seconds
    const flashAlerts = document.querySelectorAll(".alert-dismissible");
    flashAlerts.forEach((alert) => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });

    // 4. Client-side quick filter for tables
    const tableSearchInput = document.getElementById("table-quick-search");
    if (tableSearchInput) {
        tableSearchInput.addEventListener("keyup", function () {
            const query = this.value.toLowerCase();
            const targetTable = document.querySelector(".filterable-table tbody");
            if (targetTable) {
                const rows = targetTable.querySelectorAll("tr");
                rows.forEach((row) => {
                    const text = row.innerText.toLowerCase();
                    row.style.display = text.includes(query) ? "" : "none";
                });
            }
        });
    }

    // 5. Confirmation for critical actions
    document.querySelectorAll("[data-confirm]").forEach((el) => {
        el.addEventListener("click", function (e) {
            const message = this.getAttribute("data-confirm") || "Are you sure you want to proceed?";
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});
