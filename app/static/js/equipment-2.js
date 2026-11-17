function openEquipmentHelperLightbox(src, altText) {
    const modal = document.getElementById("equipmentHelperLightbox");
    const image = document.getElementById("equipmentHelperLightboxImage");
    image.src = src;
    image.alt = altText || "Φωτογραφία Εξοπλισμού";
    modal.classList.add("is-open");
    document.body.style.overflow = "hidden";
}

function closeEquipmentHelperLightbox(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById("equipmentHelperLightbox");
    const image = document.getElementById("equipmentHelperLightboxImage");
    modal.classList.remove("is-open");
    image.src = "";
    document.body.style.overflow = "";
}

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        const modal = document.getElementById("equipmentHelperLightbox");
        if (modal && modal.classList.contains("is-open")) {
            closeEquipmentHelperLightbox();
        }
    }
});
