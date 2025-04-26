document.addEventListener('DOMContentLoaded', function () {
    const suggestionLinks = document.querySelectorAll('.add-suggestion');

    suggestionLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();

            // Get the suggestion info
            const suggestionName = this.getAttribute('data-name');
            const suggestionQuantity = this.getAttribute('data-quantity');
            const suggestionUnit = this.getAttribute('data-unit');

            // Update the respective input fields
            const foodInput = document.getElementById('foodInput');
            if (foodInput) {
                foodInput.value = suggestionName;
            }

            const quantityInput = document.getElementById("quantityInput");
            if (quantityInput) {
                quantityInput.value = suggestionQuantity;
            }

            const unitInput = document.getElementById('unitInput');
            if (unitInput) {
                unitInput.value = suggestionUnit;
            }
        });
    });
});