document.addEventListener("DOMContentLoaded", function () {
    const imageCards = document.querySelectorAll(".image-card");

    imageCards.forEach((card) => {
        card.addEventListener("mouseenter", () => {
            card.classList.add("flipped");
        });

        card.addEventListener("mouseleave", () => {
            card.classList.remove("flipped");
        });

        card.addEventListener("click", () => {
            const title = card.getAttribute("data-title");
            const modalId = `modal${title.replace(/\s+/g, "")}`;
            const modal = new bootstrap.Modal(document.getElementById(modalId));
            modal.show();
        });
    });

    const closeButtons = document.querySelectorAll(".btn-close");
    closeButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const modal = button.closest(".modal");
            if (modal) {
                modal.classList.remove("show");
                modal.style.display = "none";
                document.body.classList.remove("modal-open");
                const backdrop = document.querySelector(".modal-backdrop");
                if (backdrop) {
                    backdrop.remove();
                }
            }
        });
    });
});
