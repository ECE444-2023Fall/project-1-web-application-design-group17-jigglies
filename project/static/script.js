document.addEventListener("DOMContentLoaded", function () {
    const dropZone = document.querySelector(".flex.flex-col.w-full.p-8");
    const fileInput = document.getElementById("file-upload");
    const uploadText = document.getElementById("upload-text");
    const imagePreview = document.getElementById("image-preview");
    const uploadIcon = document.getElementById("upload-icon");

    if (dropZone) {
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
}
    var input = document.querySelector("#tags");
    if (input){
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
    const email_input = document.querySelector('#email')
    if (email_input){
        document.getElementById('sendCode').addEventListener('click', function(event) {
            event.preventDefault();

            var email = document.getElementById('email').value;
            fetch('/send_verification_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({email: email}),
            })
            .then(response => response.json())
            .then(data => {
                showErrorTooltip(document.querySelector("#email"), data.message);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    }

// Search integration
function performSearch() {
    let query = document.getElementById('search_query').value;
    window.location.href = '/search?search_query=' + encodeURIComponent(query);
}


const searchInput = document.getElementById('search_query');
const suggestionsBox = document.getElementById('suggestions');

const search = document.querySelector('search_query')

if (search) {
    searchInput.addEventListener("input", function(event) {
        const value = event.target.value;
        suggestionsBox.innerHTML = "";

        if (value === "") {
            suggestionsBox.classList.add('hidden'); // hide dropdown if input is empty
            return;
        }

        // Fetching data from the server
        fetch(`/autocomplete?search_query=${value}`)
        .then(response => response.json())
        .then(data => {
            if(data.length) { // check if there are suggestions
                suggestionsBox.classList.remove('hidden'); // show dropdown if there are suggestions
            } else {
                suggestionsBox.classList.add('hidden'); // hide dropdown if there are no suggestions
            }

            // Create a <ul> element
            const ulElement = document.createElement("ul");
            ulElement.classList.add("text-sm", "text-gray-700", "dark:text-gray-200", "border-2", "border-blue-500", "rounded-lg", "shadow-2xl");

            for (let item of data) {
                const liElement = document.createElement("li");
                liElement.textContent = item.name;
                liElement.classList.add( "hover:bg-gray-200", "cursor-pointer", "px-4" , 'py-2','hover:bg-gray-100', 'dark:hover:bg-gray-600', 'dark:hover:text-white',"rounded-lg");

                liElement.addEventListener("click", function() {
                    searchInput.value = item.name;
                    suggestionsBox.innerHTML = "";
                    suggestionsBox.classList.add('hidden'); // hide dropdown after selection
                    performSearch();
                });

                ulElement.appendChild(liElement);
            }

            suggestionsBox.appendChild(ulElement);
        })
        .catch(error => {
            console.error("Error fetching search results:", error);
        });
    });
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
    var input = document.getElementById('location');
    if (input){
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
    }
});

function like(event_id) {
    const likeCount = document.getElementById("like-count")
    const likeButton = document.getElementById("like-button")
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

function performSearch(event) {
    if (event && event.key === "Enter") {
        event.preventDefault();  // prevent the default behavior of Enter key
        let query = document.getElementById('search_query').value;
        window.location.href = '/search?search_query=' + encodeURIComponent(query);
    }
}