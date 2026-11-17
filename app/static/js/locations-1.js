function toggleLocationEdit(id) {

    const form =
        document.getElementById(
            "locationEdit" + id
        );

    form.hidden =
        !form.hidden;

}
