document.addEventListener('DOMContentLoaded', function () {
    // Show the loader on page load
    document.getElementById('loader').style.visibility = 'visible';

    // Check the network speed and display loader accordingly
    if (navigator.connection) {
        const effectiveType = navigator.connection.effectiveType;

        // Loader logic based on connection speed
        if (effectiveType === '4g') {
            // Fast internet, hide loader immediately
            setTimeout(() => {
                document.getElementById('loader').style.visibility = 'hidden';
            }, 500); // Delay to give it some time to show
        } else {
            // Slow internet, keep loader visible for a longer time
            setTimeout(() => {
                document.getElementById('loader').style.visibility = 'hidden';
            }, 3000); // 3 seconds
        }
    } else {
        // Default behavior for browsers that don't support navigator.connection
        setTimeout(() => {
            document.getElementById('loader').style.visibility = 'hidden';
        }, 2000); // 2 seconds
    }

    // Initialize flatpickr
    const today = new Date();
    const formattedToday = today.toISOString().split('T')[0];

    flatpickr("#start_date", {
        minDate: formattedToday,
        dateFormat: "Y-m-d",
        onChange: function (selectedDates) {
            const endDatePicker = flatpickr("#end_date");
            endDatePicker.set("minDate", selectedDates[0]);
        },
    });

    flatpickr("#end_date", {
        minDate: formattedToday,
        dateFormat: "Y-m-d",
    });
});