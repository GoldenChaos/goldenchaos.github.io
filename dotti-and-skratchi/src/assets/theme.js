const themeClasses = ["theme-dotti", "theme-skratchi"];

document.querySelectorAll("[data-theme]").forEach((trigger) => {
  trigger.addEventListener("click", () => {
    document.body.classList.remove(...themeClasses);
    document.body.classList.add(trigger.dataset.theme);
  });
});
