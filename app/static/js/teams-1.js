function toggleTeamEdit(teamId) {

    const form =
        document.getElementById(
            "team-edit-" + teamId
        );

    if (!form) {
        return;
    }

    form.style.display =
        form.style.display === "none"
            ? "grid"
            : "none";

}

function toggleDestinationEdit(destinationId) {
    const form = document.getElementById("destination-edit-" + destinationId);
    if (!form) return;
    form.style.display = form.style.display === "none" ? "grid" : "none";
}
