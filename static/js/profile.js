document.addEventListener("DOMContentLoaded", () => {
  const tabButtons = document.querySelectorAll(".profile-tabs .tab-btn");
  const tabPanels = document.querySelectorAll(".tab-content .tab-panel");

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      // Remove active class from all buttons and panels
      tabButtons.forEach((b) => b.classList.remove("active"));
      tabPanels.forEach((panel) => panel.classList.remove("active"));

      // Activate clicked button and target tab
      btn.classList.add("active");
      const targetTabId = btn.getAttribute("data-tab");
      const targetPanel = document.getElementById(targetTabId);

      if (targetPanel) {
        targetPanel.classList.add("active");
      }
    });
  });
});
