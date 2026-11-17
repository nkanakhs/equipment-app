function openReturnComment(button) {
    const modal = document.getElementById("returnCommentModal");
    const text = document.getElementById("returnCommentText");
    text.textContent = button.dataset.returnComment || "—";
    modal.classList.add("is-open");
}

function closeReturnComment(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById("returnCommentModal").classList.remove("is-open");
}

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        const modal = document.getElementById("returnCommentModal");
        if (modal) modal.classList.remove("is-open");
    }
});
