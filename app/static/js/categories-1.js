function toggleCategoryEdit(id) {

    const form =
        document.getElementById(
            "categoryEdit" + id
        );

    form.hidden =
        !form.hidden;

}
