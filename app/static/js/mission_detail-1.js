document.addEventListener(
    "DOMContentLoaded",
    function () {

        const today =
            new Date()
                .toISOString()
                .split("T")[0];

        document
            .querySelectorAll(
                ".today-date"
            )
            .forEach(
                function (input) {

                    if (!input.value) {
                        input.value = today;
                    }

                }
            );

        updateMissionSelectionCount();

    }
);


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

    document
        .querySelectorAll(
            ".mission-equipment-checkbox"
        )
        .forEach(
            function (checkbox) {
                checkbox.checked = source.checked;
            }
        );

    updateMissionSelectionCount();

}
