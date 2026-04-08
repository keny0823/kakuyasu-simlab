document.addEventListener("DOMContentLoaded", () => {
  const brandMap = {
    ahamo: { label: "ah", className: "brand-ahamo" },
    "楽天モバイル": { label: "楽", className: "brand-rakuten" },
    LINEMO: { label: "LI", className: "brand-linemo" },
    "UQモバイル": { label: "UQ", className: "brand-uqmobile" },
    "povo2.0": { label: "po", className: "brand-povo" },
    "ワイモバイル": { label: "YM", className: "brand-ymobile" },
    IIJmio: { label: "IIJ", className: "brand-iijmio" },
    mineo: { label: "mi", className: "brand-mineo" },
    "J:COMモバイル": { label: "J:C", className: "brand-jcom" },
    "日本通信SIM": { label: "日通", className: "brand-nihontsushin" },
    "NUROモバイル": { label: "NU", className: "brand-nuro" },
  };

  document.querySelectorAll(".summary-card").forEach((card) => {
    const title = card.querySelector("strong")?.textContent?.trim();
    const mark = card.querySelector(".summary-card-mark");
    const brand = title && brandMap[title];
    if (!brand || !mark) return;
    mark.textContent = brand.label;
    mark.classList.add(brand.className);
  });

  document.querySelectorAll(".plan-card-brand").forEach((block) => {
    const title = block.querySelector("h3")?.textContent?.trim();
    const mark = block.querySelector(".carrier-mark");
    const brand = title && brandMap[title];
    if (!brand || !mark) return;
    mark.textContent = brand.label;
    mark.classList.add(brand.className);
  });
});
