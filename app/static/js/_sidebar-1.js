(function () {

    const stored =
        Number(
            localStorage.getItem(
                "equipmentLibraryFontScale"
            )
        );

    const safeValue =
        (
            Number.isFinite(stored)
            && stored >= 90
            && stored <= 150
        )
        ? stored
        : 100;

    document.documentElement.style.setProperty(
        "--app-font-scale",
        String(
            safeValue / 100
        )
    );

})();
