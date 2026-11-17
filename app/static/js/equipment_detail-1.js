function openEquipmentLightbox(src, altText) {
    const modal = document.getElementById("equipmentLightbox");
    const image = document.getElementById("equipmentLightboxImage");
    image.src = src;
    image.alt = altText || "Φωτογραφία Εξοπλισμού";
    modal.classList.add("is-open");
    document.body.style.overflow = "hidden";
}

function closeEquipmentLightbox(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById("equipmentLightbox");
    const image = document.getElementById("equipmentLightboxImage");
    modal.classList.remove("is-open");
    image.src = "";
    document.body.style.overflow = "";
}

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        const modal = document.getElementById("equipmentLightbox");
        if (modal && modal.classList.contains("is-open")) {
            closeEquipmentLightbox();
        }
    }
});
