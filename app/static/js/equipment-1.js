(function () {

    const rows = Array.from(
        document.querySelectorAll(".equipment-browser-row")
    );

    if (!rows.length) {
        return;
    }


    const el = {
        codeBadge: document.getElementById("inspectorCode"),
        title: document.getElementById("inspectorTitle"),
        subtitle: document.getElementById("inspectorSubtitle"),
        edit: document.getElementById("inspectorEdit"),
        mainPhoto: document.getElementById("inspectorMainPhoto"),
        noPhoto: document.getElementById("inspectorNoPhoto"),
        equipmentPhotoButton: document.getElementById("equipmentPhotoButton"),
        equipmentPhotoThumb: document.getElementById("equipmentPhotoThumb"),
        locationPhotoButton: document.getElementById("locationPhotoButton"),
        locationPhotoThumb: document.getElementById("locationPhotoThumb"),
        status: document.getElementById("inspectorStatus"),
        detailCode: document.getElementById("detailCode"),
        description: document.getElementById("detailDescription"),
        manufacturer: document.getElementById("detailManufacturer"),
        model: document.getElementById("detailModel"),
        serial: document.getElementById("detailSerial"),
        category: document.getElementById("detailCategory"),
        dei: document.getElementById("detailDei"),
        tem: document.getElementById("detailTem"),
        quantity: document.getElementById("detailQuantity"),
        location: document.getElementById("detailLocation"),
        notes: document.getElementById("detailNotes"),
        alternatives: document.getElementById("detailAlternatives"),
        fullCardLink: document.getElementById("fullCardLink")
    };

    let currentEquipmentPhoto = "";
    let currentLocationPhoto = "";
    let currentTitle = "";

    function safe(value) {
        return value && String(value).trim()
            ? String(value)
            : "—";
    }

    function statusClass(status) {

        if (status === "Διαθέσιμο") {
            return "status available";
        }

        if (status === "Σε Χρήση") {
            return "status usage";
        }

        if (status === "Σε Συντήρηση") {
            return "status service";
        }

        if (status === "Εκτός Λειτουργίας") {
            return "status out-of-service";
        }

        return "status";

    }

    function showMainPhoto(url, alt) {

        if (url) {

            el.mainPhoto.src = url;
            el.mainPhoto.alt = alt || "";
            el.mainPhoto.style.display = "block";
            el.noPhoto.style.display = "none";

        } else {

            el.mainPhoto.removeAttribute("src");
            el.mainPhoto.style.display = "none";
            el.noPhoto.style.display = "flex";

        }

    }

    function configurePhotoButton(
        button,
        image,
        url
    ) {

        if (url) {

            image.src = url;
            image.style.display = "block";
            button.disabled = false;

        } else {

            image.removeAttribute("src");
            image.style.display = "none";
            button.disabled = true;

        }

    }

    async function loadEquipment(row) {

        rows.forEach(function (currentRow) {
            currentRow.classList.remove("selected");
        });

        row.classList.add("selected");

        try {

            const equipmentId = row.dataset.id;

            const response = await fetch(
                "/api/equipment/" + equipmentId,
                {
                    cache: "no-store"
                }
            );

            if (!response.ok) {
                throw new Error("load failed");
            }

            const data = await response.json();

            currentEquipmentPhoto =
                data.equipment_photo_url || "";

            currentLocationPhoto =
                data.location_photo_url || "";

            currentTitle =
                data.description || "";

            el.codeBadge.textContent =
                safe(data.code);

            el.title.textContent =
                safe(data.description);

            const subtitle = [
                data.manufacturer,
                data.model
            ].filter(Boolean);

            el.subtitle.textContent =
                subtitle.length
                    ? subtitle.join(" · ")
                    : "Στοιχεία εξοπλισμού";

            el.edit.href =
                "/equipment/"
                + data.id
                + "/edit";

            el.fullCardLink.href =
                "/equipment/"
                + data.id;

            el.status.className =
                statusClass(data.status);

            el.status.textContent =
                safe(data.status);

            el.detailCode.textContent =
                safe(data.code);

            el.description.textContent =
                safe(data.description);

            el.manufacturer.textContent =
                safe(data.manufacturer);

            el.model.textContent =
                safe(data.model);

            el.serial.textContent =
                safe(data.serial_number);

            el.category.textContent =
                safe(data.category);

            el.dei.textContent =
                safe(data.dei_registry_number);

            el.tem.textContent =
                safe(data.tem_internal_code);

            el.quantity.textContent =
                data.quantity || 1;

            el.location.textContent =
                safe(data.location);

            el.notes.textContent = safe(data.notes);

            el.alternatives.innerHTML = "";
            if (data.alternatives && data.alternatives.length) {
                data.alternatives.forEach(function (alt, index) {
                    const button = document.createElement("button");
                    button.type = "button";
                    button.className = "equipment-alternative-link";
                    button.textContent = (index + 1) + ". " + alt.code + " — " + alt.description;
                    button.addEventListener("click", function () { openAlternativeInspector(alt.id); });
                    el.alternatives.appendChild(button);
                });
            } else {
                el.alternatives.textContent = "—";
            }

            configurePhotoButton(
                el.equipmentPhotoButton,
                el.equipmentPhotoThumb,
                currentEquipmentPhoto
            );

            configurePhotoButton(
                el.locationPhotoButton,
                el.locationPhotoThumb,
                currentLocationPhoto
            );

            el.equipmentPhotoButton.classList.add(
                "active"
            );

            el.locationPhotoButton.classList.remove(
                "active"
            );

            showMainPhoto(
                currentEquipmentPhoto
                    || currentLocationPhoto,
                currentTitle
            );

        } catch (error) {

            console.error(error);

        }

    }


    el.mainPhoto.addEventListener(
        "click",
        function () {
            if (
                !el.mainPhoto.src
                || el.mainPhoto.style.display === "none"
            ) {
                return;
            }

            openEquipmentHelperLightbox(
                el.mainPhoto.src,
                el.mainPhoto.alt || currentTitle || "Φωτογραφία Εξοπλισμού"
            );
        }
    );

    el.equipmentPhotoButton.addEventListener(
        "click",
        function () {

            if (!currentEquipmentPhoto) {
                return;
            }

            el.equipmentPhotoButton.classList.add(
                "active"
            );

            el.locationPhotoButton.classList.remove(
                "active"
            );

            showMainPhoto(
                currentEquipmentPhoto,
                currentTitle
            );

        }
    );

    el.locationPhotoButton.addEventListener(
        "click",
        function () {

            if (!currentLocationPhoto) {
                return;
            }

            el.locationPhotoButton.classList.add(
                "active"
            );

            el.equipmentPhotoButton.classList.remove(
                "active"
            );

            showMainPhoto(
                currentLocationPhoto,
                "Φωτογραφία θέσης αποθήκευσης"
            );

        }
    );

    rows.forEach(function (row) {

        row.addEventListener(
            "click",
            function () {
                loadEquipment(row);
            }
        );

        row.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter"
                    || event.key === " "
                ) {

                    event.preventDefault();
                    loadEquipment(row);

                }

            }
        );

    });

    const initialRow =
        document.querySelector(
            ".equipment-browser-row.selected"
        )
        || rows[0];

    loadEquipment(initialRow);

})();
