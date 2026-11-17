document.addEventListener(
    "DOMContentLoaded",
    function () {

        const backdrop =
            document.getElementById(
                "appConfirmBackdrop"
            );

        const messageElement =
            document.getElementById(
                "appConfirmMessage"
            );

        const cancelButton =
            document.getElementById(
                "appConfirmCancel"
            );

        const acceptButton =
            document.getElementById(
                "appConfirmAccept"
            );

        if (
            !backdrop
            || !messageElement
            || !cancelButton
            || !acceptButton
        ) {
            return;
        }

        let pendingForm = null;

        function extractConfirmMessage(
            inlineHandler
        ) {

            if (!inlineHandler) {
                return "Θέλεις να συνεχίσεις;";
            }

            const singleQuoteMatch =
                inlineHandler.match(
                    /confirm\('([^']*)'\)/
                );

            if (
                singleQuoteMatch
                && singleQuoteMatch[1]
            ) {
                return singleQuoteMatch[1];
            }

            const doubleQuoteMatch =
                inlineHandler.match(
                    /confirm\("([^"]*)"\)/
                );

            if (
                doubleQuoteMatch
                && doubleQuoteMatch[1]
            ) {
                return doubleQuoteMatch[1];
            }

            return "Θέλεις να συνεχίσεις;";

        }

        function openConfirm(
            form,
            message
        ) {

            pendingForm = form;

            messageElement.textContent =
                message;

            backdrop.classList.add(
                "show"
            );

            backdrop.setAttribute(
                "aria-hidden",
                "false"
            );

            document.body.classList.add(
                "app-modal-open"
            );

            setTimeout(
                function () {
                    cancelButton.focus();
                },
                30
            );

        }

        function closeConfirm() {

            pendingForm = null;

            backdrop.classList.remove(
                "show"
            );

            backdrop.setAttribute(
                "aria-hidden",
                "true"
            );

            document.body.classList.remove(
                "app-modal-open"
            );

        }

        document
            .querySelectorAll(
                'form[onsubmit*="confirm("]'
            )
            .forEach(
                function (form) {

                    const inlineHandler =
                        form.getAttribute(
                            "onsubmit"
                        );

                    const message =
                        extractConfirmMessage(
                            inlineHandler
                        );

                    form.removeAttribute(
                        "onsubmit"
                    );

                    form.dataset.confirmMessage =
                        message;

                    form.addEventListener(
                        "submit",
                        function (event) {

                            if (
                                form.dataset.confirmed
                                === "1"
                            ) {
                                return;
                            }

                            event.preventDefault();

                            openConfirm(
                                form,
                                form.dataset.confirmMessage
                            );

                        }
                    );

                }
            );

        cancelButton.addEventListener(
            "click",
            closeConfirm
        );

        acceptButton.addEventListener(
            "click",
            function () {

                if (!pendingForm) {
                    closeConfirm();
                    return;
                }

                const formToSubmit =
                    pendingForm;

                formToSubmit.dataset.confirmed =
                    "1";

                closeConfirm();

                if (
                    typeof formToSubmit.requestSubmit
                    === "function"
                ) {
                    formToSubmit.requestSubmit();
                } else {
                    formToSubmit.submit();
                }

            }
        );

        backdrop.addEventListener(
            "click",
            function (event) {

                if (
                    event.target
                    === backdrop
                ) {
                    closeConfirm();
                }

            }
        );

        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Escape"
                    && backdrop.classList.contains(
                        "show"
                    )
                ) {
                    closeConfirm();
                }

            }
        );

    }
);
