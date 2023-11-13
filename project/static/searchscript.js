document.addEventListener('DOMContentLoaded', function () {
    // Initialize flatpickr for the start date
    flatpickr("#start-date", {
        altInput: true,
        altFormat: "F j, Y", 
        dateFormat: "Y-m-d",
        onChange: function(selectedDates, dateStr, instance) {
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
            start: document.getElementById('start-date').value,
            end: document.getElementById('end-date').value
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

    displayEvents(filteredEvents);
    
}

function matchesFilters(event, filters) {
    // Date Range Filter
    let matchesDateRange = true; 
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
    let matchesOrganizers = filters.organizers.length === 0 || filters.organizers.includes(event.organizer);

    // Allow Comments Filter
    let matchesComments = true;
    if (filters.allowComments.yes && filters.allowComments.no) {
        matchesComments = true; // If both are selected, all events match
    } else if (filters.allowComments.yes) {
        matchesComments = event.allow_comments;
    } else if (filters.allowComments.no) {
        matchesComments = !event.allow_comments;
    }
    return matchesDateRange && matchesEventTags && matchesOrganizers && matchesComments;
}


function displayEvents(filteredEvents) {
    const eventCardsContainer = document.getElementById('event-cards');
    eventCardsContainer.innerHTML = ''; 

    filteredEvents.forEach(event => {
        // Create a new div element for each event
        const eventCard = document.createElement('div');
        eventCard.className = 'bg-white border border-gray-200 rounded-lg shadow bg-gray-800 dark:border-gray-700 shadow-xl';
        eventCard.style = 'display: flex; flex-direction: column; height: 100%;';

        // Determine the source for the image
        const imageSrc = event.cover_photo ? `data:image/jpeg;base64,${event.cover_photo}` : defaultEventImageUrl;
        const eventDetailsUrl = `/event/${event.id}`;

        // Format the date and time
        const eventDateTime = new Date(event.date + 'T' + event.start_time);
        const formattedDate = eventDateTime.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        const formattedTime = eventDateTime.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });

        // Add event details to the div
        eventCard.innerHTML = `
            <img class="rounded-t-lg" src="${imageSrc}" alt="Event Image ${event.id}" style="width: 300px; height: 300px; object-fit: cover;" />
            <div class="p-5 flex-grow flex flex-col relative">
                <div class="flex-grow">
                    <a href="#"><h1 id="event_name" class="mb-2 text-3xl font-extrabold text-gray-900 mb-2 lg:text-4xl dark:text-white">${event.event_name}</h1></a>
                    <p class="mb-1 font-normal text-sm text-gray-500 dark:text-gray-300">Hosted by: ${event.organizer}</p>
                    <p class="mb-1 font-normal text-sm text-gray-500 dark:text-gray-300">${formattedDate} @ ${formattedTime}</p>
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


document.addEventListener('DOMContentLoaded', function () {
    const toggleOrganizerButton = document.getElementById('toggleOrganizerButton');
    const organizerSection = document.getElementById('filter-section-organizer');

    const toggleTagsButton = document.getElementById('toggleEventTagsButton');
    const tagsSection = document.getElementById('filter-section-event-tags');

    const toggleCommentsButton = document.getElementById('toggleComments');
    const commentsSection = document.getElementById('filter-section-1');
  
    toggleOrganizerButton.addEventListener('click', function() {
        organizerSection.classList.toggle('hidden');
        const isExpanded = toggleOrganizerButton.getAttribute('aria-expanded') === 'true';
        toggleOrganizerButton.setAttribute('aria-expanded', !isExpanded);
    });

    toggleTagsButton.addEventListener('click', function() {
        tagsSection.classList.toggle('hidden');
        const isExpanded = toggleTagsButton.getAttribute('aria-expanded') === 'true';
        toggleTagsButton.setAttribute('aria-expanded', !isExpanded);
    });

    // Add the event listener for the "Allow Comments" button
    toggleCommentsButton.addEventListener('click', function() {
        commentsSection.classList.toggle('hidden');
        const isExpanded = toggleCommentsButton.getAttribute('aria-expanded') === 'true';
        toggleCommentsButton.setAttribute('aria-expanded', !isExpanded);
    });
});

function appendToList(items, elementId, inputName) {
    const listElement = document.getElementById(elementId);
    listElement.innerHTML = ''; // Clear existing content

    items.forEach(item => {
        const checkboxDiv = document.createElement('div');
        checkboxDiv.classList.add('flex', 'items-center');

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.id = `filter-${inputName}-${item.id}`;
        input.name = `${inputName}[]`;
        input.value = item.value;
        input.classList.add('h-4', 'w-4', 'rounded', 'border-gray-300', 'text-indigo-600', 'focus:ring-indigo-500');

        const label = document.createElement('label');
        label.htmlFor = input.id;
        label.classList.add('ml-3', 'min-w-0', 'flex-1', 'text-gray-500');
        label.textContent = item; 

        checkboxDiv.appendChild(input);
        checkboxDiv.appendChild(label);
        listElement.appendChild(checkboxDiv);
    });
}