
        // Show the form when "Check Book Availability" is clicked
        document.getElementById('checkAvailabilityLink').addEventListener('click', function (e) {
            e.preventDefault();
            document.getElementById('availabilityForm').style.display = 'block';
        });

        // Function to validate the form
        function validateForm() {
            const bookName = document.getElementById('bookName').value.trim();
            const authorName = document.getElementById('authorName').value.trim();
            const errorElement = document.getElementById('formError');

            if (bookName === '' || authorName === '') {
                // Show error if fields are empty
                errorElement.style.display = 'block';
            } else {
                // Hide error and simulate submission (or send to backend)
                errorElement.style.display = 'none';
                alert(`Checking availability for "${bookName}" by "${authorName}"`);
                // You can send the data to the server here
                // Example: Use AJAX or a form submission
            }
        }
