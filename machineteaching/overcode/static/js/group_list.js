(function () {
    const container = document.getElementById("groups-container");

    if (!container) {
        return;
    }

    const cardsPerPage = Number(container.dataset.cardsPerPage || 4);
    const items = Array.from(container.querySelectorAll(".group-item-overcode"));
    const pageInfo = document.getElementById("page-info");
    const prevButton = document.querySelector("[data-overcode-page-action='prev']");
    const nextButton = document.querySelector("[data-overcode-page-action='next']");

    let currentPage = 1;
    const totalPages = Math.ceil(items.length / cardsPerPage);

    function updateButtonState() {
        if (prevButton) {
            prevButton.disabled = currentPage <= 1;
        }

        if (nextButton) {
            nextButton.disabled = currentPage >= totalPages;
        }
    }

    function showPage(page) {
        if (totalPages === 0) {
            if (pageInfo) {
                pageInfo.innerText = "0 / 0";
            }

            updateButtonState();
            return;
        }

        currentPage = page;

        const start = (page - 1) * cardsPerPage;
        const end = start + cardsPerPage;

        items.forEach(function (item, index) {
            item.hidden = index < start || index >= end;
        });

        if (pageInfo) {
            pageInfo.innerText = currentPage + " / " + totalPages;
        }

        updateButtonState();
    }

    if (prevButton) {
        prevButton.addEventListener("click", function () {
            if (currentPage > 1) {
                showPage(currentPage - 1);
            }
        });
    }

    if (nextButton) {
        nextButton.addEventListener("click", function () {
            if (currentPage < totalPages) {
                showPage(currentPage + 1);
            }
        });
    }

    showPage(currentPage);
})();
