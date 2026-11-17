document.addEventListener(
    "DOMContentLoaded",
    function () {

        const params =
            new URLSearchParams(
                window.location.search
            );

        const initialMode =
            (
                params.get("tab") === "individual"
            )
            ? "individual"
            : "missions";

        switchCheckoutMode(
            initialMode,
            false
        );

        const today = new Date();

        const year = today.getFullYear();

        const month = String(
            today.getMonth() + 1
        ).padStart(2, "0");

        const day = String(
            today.getDate()
        ).padStart(2, "0");

        const todayText =
            year + "-" + month + "-" + day;


        document
            .querySelectorAll(".today-date")
            .forEach(
                function (input) {

                    if (!input.value) {
                        input.value = todayText;
                    }

                }
            );


        const activeSearch =
            document.getElementById(
                "active-loan-search"
            );


        if (activeSearch) {

            activeSearch.addEventListener(
                "input",
                filterActiveLoans
            );

        }

    }
);



function switchCheckoutMode(
    mode,
    updateUrl = true
) {

    const individualTab =
        document.getElementById(
            "individualModeTab"
        );

    const missionsTab =
        document.getElementById(
            "missionsModeTab"
        );

    const individualPanel =
        document.getElementById(
            "individualModePanel"
        );

    const missionsPanel =
        document.getElementById(
            "missionsModePanel"
        );

    if (
        !individualTab
        || !missionsTab
        || !individualPanel
        || !missionsPanel
    ) {
        return;
    }

    const showMissions =
        mode === "missions";

    individualPanel.style.display =
        showMissions
        ? "none"
        : "";

    missionsPanel.style.display =
        showMissions
        ? ""
        : "none";

    individualTab.classList.toggle(
        "active",
        !showMissions
    );

    missionsTab.classList.toggle(
        "active",
        showMissions
    );

    if (updateUrl) {

        const url =
            new URL(
                window.location.href
            );

        url.searchParams.set(
            "tab",
            showMissions
            ? "missions"
            : "individual"
        );

        if (!showMissions) {
            url.searchParams.delete(
                "mission_id"
            );
            url.searchParams.delete(
                "mission_q"
            );
        }

        window.history.replaceState(
            {},
            "",
            url
        );

    }

}




function updateMissionSelectionCount() {

    const checkboxes =
        document.querySelectorAll(
            ".mission-equipment-checkbox"
        );

    const selected =
        document.querySelectorAll(
            ".mission-equipment-checkbox:checked"
        );

    const countLabel =
        document.getElementById(
            "missionSelectedCount"
        );

    const addButton =
        document.getElementById(
            "missionBulkAddButton"
        );

    const selectAll =
        document.getElementById(
            "missionSelectAll"
        );

    if (countLabel) {

        countLabel.textContent =
            selected.length === 1
            ? "1 επιλεγμένο"
            : selected.length + " επιλεγμένα";

    }

    if (addButton) {
        addButton.disabled =
            selected.length === 0;
    }

    if (selectAll) {

        selectAll.checked =
            checkboxes.length > 0
            && selected.length === checkboxes.length;

        selectAll.indeterminate =
            selected.length > 0
            && selected.length < checkboxes.length;

    }

}


function toggleMissionSelection(
    source
) {

    const checkboxes =
        document.querySelectorAll(
            ".mission-equipment-checkbox"
        );

    checkboxes.forEach(
        function (checkbox) {
            checkbox.checked =
                source.checked;
        }
    );

    updateMissionSelectionCount();

}


function syncMissionPlate() {

    const select =
        document.getElementById(
            "missionVehicleSelect"
        );

    const plateInput =
        document.getElementById(
            "missionPlateInput"
        );

    if (!select || !plateInput) {
        return;
    }

    const option =
        select.options[
            select.selectedIndex
        ];

    plateInput.value =
        option
        ? (
            option.getAttribute(
                "data-plate"
            )
            || ""
        )
        : "";

}


function filterActiveLoans() {

    const input =
        document.getElementById(
            "active-loan-search"
        );

    if (!input) {
        return;
    }

    const query =
        input.value
            .trim()
            .toLowerCase();

    const cards =
        document.querySelectorAll(
            ".active-loan-card"
        );

    let visibleCount = 0;


    cards.forEach(
        function (card) {

            const searchText =
                card
                    .getAttribute("data-search")
                    .toLowerCase();

            if (searchText.includes(query)) {

                card.style.display = "";
                visibleCount++;

            } else {

                card.style.display = "none";

            }

        }
    );


    const noResults =
        document.getElementById(
            "no-active-results"
        );


    if (noResults) {

        noResults.style.display =
            (
                query !== ""
                && visibleCount === 0
            )
            ? "block"
            : "none";

    }

}


function clearActiveLoanSearch() {

    const input =
        document.getElementById(
            "active-loan-search"
        );

    if (!input) {
        return;
    }

    input.value = "";

    filterActiveLoans();

    input.focus();

}
