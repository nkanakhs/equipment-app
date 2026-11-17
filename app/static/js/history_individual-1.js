function toggleHistoryExportMode() {

    document.body.classList.toggle(
        "history-export-mode"
    );

    const active =
        document.body.classList.contains(
            "history-export-mode"
        );

    const bar =
        document.getElementById(
            "historyExportBar"
        );

    const toggle =
        document.getElementById(
            "historyExportToggle"
        );

    if (bar) {
        bar.style.display =
            active
            ? "flex"
            : "none";
    }

    if (toggle) {
        toggle.textContent =
            active
            ? "Κλείσιμο Export"
            : "Export";
    }

    if (!active) {
        clearHistoryExportSelection();
    }

}


function clearHistoryExportSelection() {

    document
        .querySelectorAll(
            ".history-export-checkbox"
        )
        .forEach(
            function (checkbox) {
                checkbox.checked = false;
            }
        );

    updateHistoryExportCount();

}


function cancelHistoryExport() {

    document.body.classList.remove(
        "history-export-mode"
    );

    const bar =
        document.getElementById(
            "historyExportBar"
        );

    const toggle =
        document.getElementById(
            "historyExportToggle"
        );

    if (bar) {
        bar.style.display = "none";
    }

    if (toggle) {
        toggle.textContent = "Export";
    }

    clearHistoryExportSelection();

}


function updateHistoryExportCount() {

    const checked =
        document.querySelectorAll(
            ".history-export-checkbox:checked"
        ).length;

    const count =
        document.getElementById(
            "historyExportCount"
        );

    const submit =
        document.getElementById(
            "historyExportSubmit"
        );

    if (count) {
        count.textContent =
            checked
            + (
                checked === 1
                ? " επιλεγμένη"
                : " επιλεγμένες"
            );
    }

    if (submit) {
        submit.disabled =
            checked === 0;
    }

}
