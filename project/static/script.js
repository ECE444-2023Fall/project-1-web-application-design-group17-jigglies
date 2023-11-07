document.addEventListener("DOMContentLoaded", function () {
    const dropZone = document.querySelector(".flex.flex-col.w-full.p-8");
    const fileInput = document.getElementById("file-upload");
    const uploadText = document.getElementById("upload-text");
    const imagePreview = document.getElementById("image-preview");
    const uploadIcon = document.getElementById("upload-icon");

    if (!dropZone) {
        console.error("Drop zone element not found!");
        return;
    }

    dropZone.addEventListener("dragover", function (e) {
        e.preventDefault();
    });

    dropZone.addEventListener("drop", function (e) {
        e.preventDefault();

        if (e.dataTransfer.items && e.dataTransfer.items[0].kind === "file") {
            const file = e.dataTransfer.items[0].getAsFile();
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
            previewImage(file);
        }
    });

    fileInput.addEventListener("change", function () {
        const file = fileInput.files[0];
        if (file) {
            previewImage(file);
        }
    });

    function previewImage(file) {
        const reader = new FileReader();
        reader.onload = function (e) {
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
    tagify.on('input', function (e) {
        if (tagify.value.length >= tagify.settings.maxTags) {
            showErrorTooltip(input, 'You have reached the maximum number of allowed tags!');
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
            google.maps.event.addListener(autocomplete, 'place_changed', function () {
                var place = autocomplete.getPlace();
                if (!place.place_id) {
                    showErrorTooltip(input, "Please select a valid location from the dropdown.");
                    input.value = "";  // Clear the input
                }
            });
        }
    }
    // Get the start and end time select elements
    const startTimeSelect = document.getElementById('start-time');
    const endTimeSelect = document.getElementById('end-time');

    // Function to check and validate times
    function validateTimes() {
        const startTimeValue = parseInt(startTimeSelect.value, 10);
        const endTimeValue = parseInt(endTimeSelect.value, 10);

        if (endTimeValue <= startTimeValue) {
            showErrorTooltip(endTimeSelect, 'End time should be after start time');
            endTimeSelect.value = ''; // Clear the end time selection
        }
    }

    // Add event listeners to check the times whenever they change
    startTimeSelect.addEventListener('change', validateTimes);
    endTimeSelect.addEventListener('change', validateTimes);

    // Call the initialize function when the window loads.
    google.maps.event.addDomListener(window, 'load', initialize);
});

function like(event_id) {
    const likeCount = document.getElementById("like-count");
    const heartIcon = document.getElementById("heart-icon");

    fetch(`/like_event/${event_id}`, { method: "POST" }).then((res) => res.json()).then((data) => {
        likeCount.innerHTML = data["like_count"]
        if (data["user_has_liked"] === true) {
            heartIcon.classList.remove("fa-regular");
            heartIcon.classList.add("fa-solid");
        }
        else {
            heartIcon.classList.remove("fa-solid");
            heartIcon.classList.add("fa-regular");
        }
    });
}

function rsvp(event_id) {
    const rsvpButton = document.getElementById("rsvp-button");

    fetch(`/rsvp_event/${event_id}`, { method: "POST" }).then((res) => res.json()).then((data) => {
        if (data["user_has_rsvp"] === true) {
            rsvpButton.classList.remove("text-purple-700");
            rsvpButton.classList.add("text-white", "bg-purple-700");
            rsvpButton.innerHTML = "RSVP'd";
        }
        else {
            rsvpButton.classList.remove("text-white", "bg-purple-700");
            rsvpButton.classList.add("text-purple-700");
            rsvpButton.innerHTML = "RSVP";
        }
    });
}