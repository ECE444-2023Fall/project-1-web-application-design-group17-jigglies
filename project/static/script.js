document.addEventListener("DOMContentLoaded", function() {
    const dropZone = document.querySelector(".flex.flex-col.w-full.p-8");
    const fileInput = document.getElementById("file-upload");
    const uploadText = document.getElementById("upload-text");
    const imagePreview = document.getElementById("image-preview");
    const uploadIcon = document.getElementById("upload-icon");

    if (!dropZone) {
        console.error("Drop zone element not found!");
        return;
    }

    dropZone.addEventListener("dragover", function(e) {
        e.preventDefault();
    });

    dropZone.addEventListener("drop", function(e) {
        e.preventDefault();

        if (e.dataTransfer.items && e.dataTransfer.items[0].kind === "file") {
            const file = e.dataTransfer.items[0].getAsFile();
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
            previewImage(file);
        }
    });

    fileInput.addEventListener("change", function() {
        const file = fileInput.files[0];
        if (file) {
            previewImage(file);
        }
    });

    function previewImage(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.classList.remove("hidden");
            uploadIcon.classList.add("hidden");
            uploadText.textContent = "Replace image";
        };
        reader.readAsDataURL(file);
    }
function showErrorTooltip(inputElement, message) {
        // Create a tippy instance
        const tip = tippy(inputElement, {
            content: message,
            trigger: 'manual',  
            placement: 'top' 
        });
    
        // Show the tooltip
        tip.show();
    
        // Hide the tooltip after a delay (e.g., 5 seconds)
        setTimeout(() => {
            tip.hide();
            tip.destroy(); // Properly clean up the tippy instance
        }, 5000);
    }

// Search integration
function performSearch() {
    let query = document.getElementById('search_query').value;
    window.location.href = '/search?search_query=' + encodeURIComponent(query);
}


// Autocomplete Integration
const searchInput = document.getElementById('search_query');
const suggestionsBox = document.getElementById('suggestions');

searchInput.addEventListener("input", function(event) {
    const value = event.target.value;
    suggestionsBox.innerHTML = "";

    if (value === "") return;  // Don't show suggestions if the input is empty

    // Fetching data from the server
    fetch(`/autocomplete?search_query=${value}`)
    .then(response => response.json())
    .then(data => {
        for (let item of data) {
            const suggestionItem = document.createElement("div");
            suggestionItem.textContent = item.name; 
            suggestionItem.classList.add("p-2", "hover:bg-gray-200", "cursor-pointer", "border", "border-gray-300", "rounded");
            suggestionItem.addEventListener("click", function() {
                searchInput.value = item.name;
                suggestionsBox.innerHTML = "";
                performSearch();
            });
            suggestionsBox.appendChild(suggestionItem);
        }
    })
    .catch(error => {
        console.error("Error fetching search results:", error);
    });
});

function initialize() {
    var input = document.getElementById('location');
    if (input) {
        var options = {
            componentRestrictions: { country: 'CA' }  // Restrict results to Canada
        };

        var autocomplete = new google.maps.places.Autocomplete(input, options);

        // Bias results towards Toronto 
        var torontoBounds = new google.maps.LatLngBounds(
            new google.maps.LatLng(43.5800, -79.6393), // Southwest corner of Toronto
            new google.maps.LatLng(43.8555, -79.1169)  // Northeast corner of Toronto
        );
        autocomplete.setBounds(torontoBounds);

        // Add an event listener for place_changed
        google.maps.event.addListener(autocomplete, 'place_changed', function() {
            var place = autocomplete.getPlace();
            if (!place.place_id) {
                showErrorTooltip(input, "Please select a valid location from the dropdown.");
                input.value = "";  // Clear the input
            }
        });
    }
}

// Call the initialize function when the window loads.
google.maps.event.addDomListener(window, 'load', initialize);
});