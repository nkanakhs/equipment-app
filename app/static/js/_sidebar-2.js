(function () {

    const params =
        new URLSearchParams(
            window.location.search
        );

    const message =
        params.get("toast");

    if (!message) {
        return;
    }

    const type =
        params.get("toast_type")
        || "success";

    const container =
        document.getElementById(
            "appToastContainer"
        );

    if (!container) {
        return;
    }

    const toast =
        document.createElement(
            "div"
        );

    toast.className =
        "app-toast app-toast-"
        + type;

    const icon =
        document.createElement(
            "div"
        );

    icon.className =
        "app-toast-icon";

    icon.textContent =
        type === "error"
            ? "!"
            : "✓";

    const content =
        document.createElement(
            "div"
        );

    content.className =
        "app-toast-content";

    const title =
        document.createElement(
            "strong"
        );

    title.textContent =
        type === "error"
            ? "Προσοχή"
            : "Ολοκληρώθηκε";

    const text =
        document.createElement(
            "span"
        );

    text.textContent =
        message;

    const close =
        document.createElement(
            "button"
        );

    close.className =
        "app-toast-close";

    close.type =
        "button";

    close.setAttribute(
        "aria-label",
        "Κλείσιμο"
    );

    close.textContent =
        "×";

    content.appendChild(
        title
    );

    content.appendChild(
        text
    );

    toast.appendChild(
        icon
    );

    toast.appendChild(
        content
    );

    toast.appendChild(
        close
    );

    container.appendChild(
        toast
    );

    requestAnimationFrame(
        function () {
            toast.classList.add(
                "show"
            );
        }
    );

    function removeToast() {

        toast.classList.remove(
            "show"
        );

        setTimeout(
            function () {
                toast.remove();
            },
            240
        );

    }

    close.addEventListener(
        "click",
        removeToast
    );

    setTimeout(
        removeToast,
        3200
    );

    params.delete("toast");
    params.delete("toast_type");

    const cleanQuery =
        params.toString();

    const cleanUrl =
        window.location.pathname
        + (
            cleanQuery
                ? "?" + cleanQuery
                : ""
        )
        + window.location.hash;

    window.history.replaceState(
        {},
        document.title,
        cleanUrl
    );

})();
