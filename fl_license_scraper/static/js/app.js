/**
 * FL License Lookup - Main Application JavaScript
 */

document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });

  // License number auto-formatting
  const licenseInputs = document.querySelectorAll(
    'input[name="license_number"]'
  );
  licenseInputs.forEach(function (input) {
    input.addEventListener("input", function () {
      this.value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, "");
    });
  });

  // Star rating interactive (for review forms)
  const ratingSelects = document.querySelectorAll(
    'select[name*="_rating"], select[name="overall_rating"]'
  );
  ratingSelects.forEach(function (select) {
    select.classList.add("form-select");
  });

  // Confirm before submitting bids
  const bidForms = document.querySelectorAll('form[action*="/bid/"]');
  bidForms.forEach(function (form) {
    form.addEventListener("submit", function (e) {
      const amount = form.querySelector('input[name="amount"]');
      if (amount && amount.value) {
        const formatted = parseFloat(amount.value).toLocaleString("en-US", {
          style: "currency",
          currency: "USD",
        });
        if (!confirm("Submit bid for " + formatted + "?")) {
          e.preventDefault();
        }
      }
    });
  });
});
