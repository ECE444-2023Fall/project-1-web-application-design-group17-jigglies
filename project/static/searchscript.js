function appendToDropDown(optionsList, element) {
    const dropdownMenu = document.getElementById(element);

    dropdownMenu.innerHTML = '';

    optionsList.forEach(option => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `<div class="flex items-center p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-600">
                                  <input type="checkbox" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-700 dark:focus:ring-offset-gray-700 focus:ring-2 dark:bg-gray-600 dark:border-gray-500">
                                  <label class="w-full ml-2 text-sm font-medium text-gray-900 rounded dark:text-gray-300">${option}</label>
                              </div>`;
        dropdownMenu.appendChild(listItem);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    // Initialize flatpickr for the start date
    flatpickr("#start-date", {
        altInput: true, // Uses a more user-friendly date format in the input
        altFormat: "F j, Y", // User-friendly date format
        dateFormat: "Y-m-d", // Format that the actual input value is stored in
        onChange: function(selectedDates, dateStr, instance) {
            // This function is called whenever a user selects a date
            updateFilters();
        }
    });

    // Initialize flatpickr for the end date
    flatpickr("#end-date", {
        altInput: true,
        altFormat: "F j, Y",
        dateFormat: "Y-m-d",
        onChange: function(selectedDates, dateStr, instance) {
            updateFilters();
        }
    });
});

function updateFilters() {
    let filters = {
        dateRange: {
            start: document.getElementById('start-date').value, // Retrieves the start date
            end: document.getElementById('end-date').value // Retrieves the end date
        },
        eventTags: [],
        organizers: [],
        allowComments: {
            yes: document.querySelector('#filter-section-1 input[value="new-arrivals"]').checked,
            no: document.querySelector('#filter-section-1 input[value="sale"]').checked
        },
    };

    // Collecting event tag values
    document.querySelectorAll('#dropdownTags input[type="checkbox"]:checked').forEach(checkbox => {
        let label = checkbox.nextElementSibling.textContent.trim();
        filters.eventTags.push(label);
    });

    // Collecting organizer values
    document.querySelectorAll('#organizersList input[type="checkbox"]:checked').forEach(checkbox => {
        let label = checkbox.nextElementSibling.textContent.trim();
        filters.organizers.push(label);
    });

    //Apply filters to events
    let filteredEvents = allEvents.filter(event => {
        return matchesFilters(event, filters);
    });

    console.log("call events", allEvents);
    console.log('Current Filters:', filters);
    displayEvents(filteredEvents);
    
}

function matchesFilters(event, filters) {
    // Date Range Filter
    let matchesDateRange = true; // Initialize as true; replace with actual logic if needed
    if(filters.dateRange.start ){
        let eventDate = new Date(event.date);
        let startDate = new Date(filters.dateRange.start);
        matchesDateRange = eventDate >= startDate
        if (filters.dateRange.start && filters.dateRange.end) {
            let eventDate = new Date(event.date);
            let startDate = new Date(filters.dateRange.start);
            let endDate = new Date(filters.dateRange.end);
            matchesDateRange = eventDate >= startDate && eventDate <= endDate;
        }
    }


    // Event Tags Filter
    let matchesEventTags = filters.eventTags.length === 0 || filters.eventTags.some(tag => event.tags.includes(tag));

    // Organizers Filter
    let matchesOrganizers = filters.organizers.length === 0 || filters.organizers.includes(event.event_organization);

    // Allow Comments Filter
    let matchesComments = true; // Initialize as true; replace with actual logic if needed
    if (filters.allowComments.yes && filters.allowComments.no) {
        matchesComments = true; // If both are selected, all events match
    } else if (filters.allowComments.yes) {
        matchesComments = event.allow_comments;
    } else if (filters.allowComments.no) {
        matchesComments = !event.allow_comments;
    }

    // Combine all filter checks
    //return true
    return matchesDateRange && matchesEventTags && matchesOrganizers && matchesComments;
}


function displayEvents(filteredEvents) {
    const eventCardsContainer = document.getElementById('event-cards');
    eventCardsContainer.innerHTML = ''; // Clear existing events

    filteredEvents.forEach(event => {
        // Create a new div element for each event
        const eventCard = document.createElement('div');
        eventCard.className = 'bg-white border border-gray-200 rounded-lg shadow bg-gray-800 dark:border-gray-700 shadow-xl';
        eventCard.style = 'display: flex; flex-direction: column; height: 100%;';

        // Determine the source for the image
        const imageSrc = event.cover_photo ? `data:image/jpeg;base64,${event.cover_photo}` : defaultEventImageUrl;
        console.log(imageSrc)
        const eventDetailsUrl = `/event/${event.id}`;

        // Add event details to the div
        eventCard.innerHTML = `
            <img class="rounded-t-lg" src="${imageSrc}" alt="Event Image ${event.id}" style="width: 300px; height: 300px; object-fit: cover;" />
            <div class="p-5 flex-grow flex flex-col relative">
                <div class="flex-grow">
                    <a href="#"><h1 class="mb-2 text-3xl font-extrabold text-gray-900 mb-2 lg:text-4xl dark:text-white">${event.event_name}</h1></a>
                    <p class="mb-1 font-normal text-sm text-gray-500 dark:text-gray-300">Hosted by: ${event.event_organization}</p>
                    <p class="mb-1 font-normal text-sm text-gray-500 dark:text-gray-300">${event.date} @ ${event.start_time}</p>
                    <p class="mb-1 font-normal text-sm text-gray-500 dark:text-gray-300">Address: ${event.location}</p>
                    <p class="mb-3 font-normal text-gray-700 dark:text-gray-400">${event.event_information}</p>
                </div>
                <a href="${eventDetailsUrl}" class="self-start inline-flex items-center px-3 py-2 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Learn more</a>
            </div>
        `;

        // Append the new event card to the container
        eventCardsContainer.appendChild(eventCard);
    });
}


document.addEventListener('DOMContentLoaded', function () {
    // Initialize flatpickr for the start date input
    const startDateInput = document.querySelector('input[name="start"]');
    if (startDateInput) {
        flatpickr(startDateInput, {
            altInput: true,
            altFormat: "F j, Y",
            dateFormat: "Y-m-d",
            onChange: function(selectedDates, dateStr, instance) {
                updateFilters();
            }
        });
    } else {
        console.log('Start date input not found');
    }

    // Initialize flatpickr for the end date input
    const endDateInput = document.querySelector('input[name="end"]');
    if (endDateInput) {
        flatpickr(endDateInput, {
            altInput: true,
            altFormat: "F j, Y",
            dateFormat: "Y-m-d",
            onChange: function(selectedDates, dateStr, instance) {
                updateFilters();
            }
        });
    } else {
        console.log('End date input not found');
    }

    // Attaching event listeners to dropdown filters
    const dropdownTags = document.getElementById('dropdownTags');
    if (dropdownTags) {
        dropdownTags.addEventListener('change', updateFilters);
    } else {
        console.log('Dropdown tags not found');
    }

    const organizersList = document.getElementById('organizersList');
    if (organizersList) {
        organizersList.addEventListener('change', updateFilters);
    } else {
        console.log('Organizers list not found');
    }

    // Attaching event listeners to checkbox filters
    document.querySelectorAll('#filter-section-1 input[type="checkbox"]').forEach(checkbox => {
        if (checkbox) {
            checkbox.addEventListener('change', updateFilters);
        }
    });

    // Call updateFilters on page load to initialize
    updateFilters();
});
