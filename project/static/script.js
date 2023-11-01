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
    var input = document.querySelector("#tags");

    // Initialize Tagify with maxTags setting
    var tagify = new Tagify(input, {
        delimiters: ", ",
        maxTags: 5
    });
    
    // Add an event listener to notify the user when they've reached the max number of tags
    tagify.on('input', function(e){
        if(tagify.value.length >= tagify.settings.maxTags){
            showErrorTooltip(input,'You have reached the maximum number of allowed tags!');
        }
    });
    
    
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