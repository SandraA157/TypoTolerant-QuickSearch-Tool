// Function to load data from the selected JSON file and display it in the table
function loadData() {
    const selectedFile = document.getElementById('fileSelect').value;
    
    // Send a request to the backend to fetch the selected file's data
    fetch('/load_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file: selectedFile })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Data received from server:', data); // Debugging step
        populateTable(data);
    })
    .catch(error => {
        console.error('Error loading data:', error);
    });
}

// Function to populate the table with data
function populateTable(data) {
    const tableBody = document.getElementById('dataTable').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';  // Clear any existing rows
    
    // Debugging: Log the data to check if it's what you expect
    console.log('Data in populateTable:', data);

    // Make sure data is an array and has elements
    if (!Array.isArray(data) || data.length === 0) {
        console.error("Data is not an array or is empty");
        return;
    }

    // Loop through the data and insert rows
    data.forEach((item, index) => {
        const row = tableBody.insertRow();

        const questionCell = row.insertCell(0);
        questionCell.textContent = item.question || 'No question';  // Set question text

        const answerCell = row.insertCell(1);
        answerCell.textContent = item.answer || 'No answer';  // Set answer text

        const actionCell = row.insertCell(2);

        // Edit button
        const editButton = document.createElement('button');
        editButton.textContent = 'Edit';
        editButton.onclick = () => editRow(index, item); // Pass index and data
        actionCell.appendChild(editButton);
        
        // Delete button
        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.onclick = () => deleteRow(index); // Pass index
        actionCell.appendChild(deleteButton);
    });
}

// Function to edit a row
function editRow(index, item) {
    document.getElementById('Question').value = item.question;
    document.getElementById('Answer').value = item.answer;
    
    // Show the popup
    document.getElementById('editpopup').style.display = 'block';
    
    // Add event listener to save button
    document.getElementById('saveButton').onclick = () => saveEdit(index);
}

// Function to hide the edit form (popup) when Cancel is clicked
function cancelForm() {
    document.getElementById('editpopup').style.display = 'none';
}

// Function to save the edited data
function saveEdit(index) {
    const updatedQuestion = document.getElementById('Question').value;
    const updatedAnswer = document.getElementById('Answer').value;

    if (!updatedQuestion || !updatedAnswer) {
        alert("Please fill in both question and answer!");
        return;
    }

    // Send updated data to the server
    fetch('/update_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            index: index,
            question: updatedQuestion,
            answer: updatedAnswer,
            file: document.getElementById('fileSelect').value
        })
    })
    .then(response => response.json())  // Parse the JSON response
    .then(data => {
        if (data.success) {
            alert('Data updated successfully!');
            loadData(); // Reload the data to show updated content
            document.getElementById('editpopup').style.display = 'none';  // Hide the popup
        } else {
            alert('Error updating data!');
        }
    })
    .catch(error => {
        console.error('Error during fetch operation:', error);
        alert('Error occurred while processing your request.');
    });
}

// Function to delete a row
function deleteRow(index) {
    if (confirm('Are you sure you want to delete this item?')) {
        fetch('/delete_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                index: index,
                file: document.getElementById('fileSelect').value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Data deleted successfully!');
                loadData(); // Reload the data
            } else {
                alert('Error deleting data: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the data.');
        });
    }
    //refresh and load data?
}

// Function for the search feature
document.getElementById('searchBox').addEventListener('input', function () {
    const searchTerm = this.value.toLowerCase();
    const rows = document.querySelectorAll('#dataTable tbody tr');

    rows.forEach(row => {
        const question = row.cells[0].textContent.toLowerCase();
        const answer = row.cells[1].textContent.toLowerCase();

        if (question.includes(searchTerm) || answer.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

function showAlert(message, color) {
    var alertPopup = document.getElementById('alert-popup');
    var errorMessageText = document.getElementById('errorMessageText');

    // Check if the element exists before trying to access it
    if (!alertPopup || !errorMessageText) {
        console.error("Alert elements not found in the DOM.");
        return;
    }

    errorMessageText.innerText = message;
    alertPopup.style.backgroundColor = color;
    alertPopup.style.display = 'block';

    setTimeout(function () {
        alertPopup.style.display = 'none';
    }, 1000);
}


	function addNewItem() {
		var dataTable = document.getElementById('dataTable');
		var tbody = dataTable.querySelector('tbody');
        
	        // Check if tbody exists, create it if not
	        if (!tbody) {
	          tbody = document.createElement('tbody');
	          dataTable.appendChild(tbody);
	        }

	        var newRow = tbody.insertRow();

		// Get the number of columns in the first row
        	var columnCount = 2;

		newRow.insertCell(0).innerText = document.getElementById('newQuestion').value;
		newRow.insertCell(1).innerText = document.getElementById('newAnswer').value;
                
		// Add the delete and edit buttons to the last cell
		var lastCell = newRow.insertCell(columnCount);
		var editButton = document.createElement('button');
		editButton.innerHTML = 'Edit';
		editButton.className = 'edit-button'; // Set the class for styling

		editButton.addEventListener('click', function() {
		    editRow(newRow.rowIndex, newRow);  // Use row index
		});

		var deleteButton = document.createElement('button');
		deleteButton.innerHTML = 'Delete';
		deleteButton.className = 'delete-button'; // Set the class for styling
		deleteButton.addEventListener('click', function() {
		    deleteRow(newRow.rowIndex);
		});

		lastCell.appendChild(editButton);
		lastCell.appendChild(deleteButton);
            }


	function getTableData() {
	    var table = document.getElementById('dataTable');
	    var data = [];

	    for (var i = 1; i < table.rows.length; i++) { // Start from 1 to skip header row
		var row = table.rows[i];
		var rowData = {};

		for (var j = 0; j < row.cells.length - 1; j++) { // Skip the last cell with buttons
		    var cell = row.cells[j];
		    var columnName = table.rows[0].cells[j].innerText;
		    rowData[columnName] = cell.textContent.trim(); // Use trim() to remove extra whitespaces
		
		    if (columnName !== 'Action') {
		        rowData[columnName] = cell.textContent.trim();
		    }
		}

		data.push(rowData);
	    }

	    return data;
	}

	function saveData() {
	    var data = getTableData();
	    const selected_file = document.getElementById('fileSelect').value;

	    // Check if there is any data to upload
	    if (data.length > 0) {
		// Use AJAX to send data to the server
		fetch('/save_data', {
		    method: 'POST',
		    headers: {
			'Content-Type': 'application/json',
		    },
		    body: JSON.stringify({ data: data, selected_file: selected_file }),
		})

		.then(response => response.json())
		.then(data => {
		    if (data.success) {
		        showAlert('Data uploaded successfully', 'green');
		    } else {
		        showAlert(data.message || 'Upload failed', 'red');
		    }
		})
		.catch(error => {
		    console.error('Error during fetch operation:', error);
		    showAlert('Error occurred while processing your request.', 'red');
		});
	    } 	
	}
