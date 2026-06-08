const year = document.querySelector("#year");
if (year) {
  year.textContent = new Date().getFullYear();
}

const languageToggle = document.querySelector(".lang-toggle");
const translatableItems = document.querySelectorAll("[data-en][data-zh]");

function applyLanguage(language) {
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  document.title = language === "zh"
    ? "杨富祥 | 个人主页"
    : "Fuxiang Yang | Personal Homepage";

  translatableItems.forEach((item) => {
    item.textContent = item.dataset[language];
  });

  if (languageToggle) {
    languageToggle.textContent = language === "zh" ? "EN" : "中文";
    languageToggle.setAttribute(
      "aria-label",
      language === "zh" ? "Switch to English" : "切换到中文"
    );
  }

  localStorage.setItem("homepage-language", language);
}

if (languageToggle) {
  languageToggle.addEventListener("click", () => {
    const nextLanguage = document.documentElement.lang === "zh-CN" ? "en" : "zh";
    applyLanguage(nextLanguage);
  });
}

applyLanguage(localStorage.getItem("homepage-language") || "en");
