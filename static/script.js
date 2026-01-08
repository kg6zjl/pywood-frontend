// create socket
try {
    var socket = io();
    console.log('Socket.io loaded successfully');
} catch (e) {
    console.error('Failed to load Socket.io:', e);
}

// hold dark mode value
var isDarkMode = true;

// light mode / dark mode toggle
document.getElementById('mode-toggle').addEventListener('click', function() {
    isDarkMode = !isDarkMode;
    if (isDarkMode) {
        document.body.classList.remove('light-mode');
        document.querySelector('.navbar').classList.remove('light-mode');
        document.querySelectorAll('.nav-button').forEach(button => button.classList.remove('light-mode'));
        this.textContent = 'Light Mode';
    } else {
        document.body.classList.add('light-mode');
        document.querySelector('.navbar').classList.add('light-mode');
        document.querySelectorAll('.nav-button').forEach(button => button.classList.add('light-mode'));
        this.textContent = 'Dark Mode';
    }
});

// connect to websocket
socket.on('connect', function() {
    console.log('Connected to WebSocket');
});

// socket disconnect
socket.on('disconnect', function() {
    console.log('Disconnected from WebSocket');
});

// these are the live race results flowing in via websocket
socket.on('new_results', function(data) {
    document.getElementById('ready-banner').style.visibility = 'hidden'; // Hide the banner
    for (var position in data) {
        var lane = data[position];
        if (position === "first") {
            document.getElementById('first').textContent = `Lane ${lane}`;
        } else if (position === "second") {
            document.getElementById('second').textContent = `Lane ${lane}`;
        } else if (position === "third") {
            document.getElementById('third').textContent = `Lane ${lane}`;
        } else if (position === "fourth") {
            document.getElementById('fourth').textContent = `Lane ${lane}`;
        }
    }
});

// this recieves the reset and flushes the page
socket.on('reset_results', function() {
    document.getElementById('first').textContent = '';
    document.getElementById('second').textContent = '';
    document.getElementById('third').textContent = '';
    document.getElementById('fourth').textContent = '';
    document.getElementById('ready-banner').style.visibility = 'visible'; // Show the banner
});

// this is all results
function viewResults() {
    document.getElementById('view-results-button').style.display = 'none';
    document.getElementById('back-to-race-view-button').style.display = 'inline-block';
    
    document.getElementById('results-header').style.display = 'block';
    fetch('/results')
        .then(response => response.json())
        .then(data => {
            const resultsTable = document.getElementById('results');
            resultsTable.innerHTML = '';  // Clear previous results
            data.forEach(result => {
                const row = document.createElement('tr');
                const first = result.first ? `Lane ${result.first}` : "---";
                const second = result.second ? `Lane ${result.second}` : "---";
                const third = result.third ? `Lane ${result.third}` : "---";
                const fourth = result.fourth ? `Lane ${result.fourth}` : "---";
                
                row.innerHTML = `
                    <td class="race-id" onclick="viewRaceDetails(${result.id})">${result.id}</td>
                    <td>${first}</td>
                    <td>${second}</td>
                    <td>${third}</td>
                    <td>${fourth}</td>
                `;
                resultsTable.appendChild(row);
            });
            document.getElementById('race-view').style.display = 'none';
            document.getElementById('results-container').style.display = 'block';
        });
}

// this is the view for a single race
function viewRaceDetails(raceId) {
    fetch(`/results/${raceId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }

            console.log('Race data:', data);  // Add this line to inspect the data
            
            document.getElementById('race-id').textContent = `Race ID: ${data.id}`;
            document.getElementById('race-date').textContent = `Date: ${new Date(data.date).toLocaleString()}`;
            
            const raceDetailsBody = document.getElementById('race-details-body');
            raceDetailsBody.innerHTML = '';  // Clear previous race details

            const positions = ['first', 'second', 'third', 'fourth'];
            positions.forEach(position => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${capitalizeFirstLetter(position)}</td>
                    <td>${data[position] ? `Lane ${data[position]}` : "---"}</td>
                `;
                raceDetailsBody.appendChild(row);
            });
            
            document.getElementById('results-container').style.display = 'none';
            document.getElementById('race-details-container').style.display = 'block';
            document.getElementById('results-header').style.display = 'none';
            document.getElementById('back-to-results-button').style.display = 'inline-block';
            document.getElementById('back-to-race-view-button').style.display = 'inline-block';
        })
        .catch(error => console.error('Error fetching race details:', error));
}

// caps handler
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// hide/show nav/elements as page changes
function goRaceView() {
    document.getElementById('view-results-button').style.display = 'inline-block';
    document.getElementById('back-to-race-view-button').style.display = 'none';    
    document.getElementById('results-header').style.display = 'none';
    document.getElementById('results-container').style.display = 'none';
    document.getElementById('race-view').style.display = 'block';
    document.getElementById('race-details-container').style.display = 'none';
}

// hide/show nav/elements as page changes
function goBackToResults() {
    document.getElementById('race-details-container').style.display = 'none';
    document.getElementById('results-container').style.display = 'block';
    document.getElementById('results-header').style.display = 'block';  // Show previous results header
    document.getElementById('back-to-results-button').style.display = 'none';  // Hide back to results button
    document.getElementById('back-to-race-view-button').style.display = 'inline-block';  // Show back to race view button
}

// trigger a server-side race reset
function resetRace() {
    const confirmReset = confirm('Reset race and clear current results?');
    if (!confirmReset) return;
    fetch('/api/v1/reset', { method: 'POST' })
        .then(res => {
            if (!res.ok) {
                throw new Error('Failed to reset race');
            }
            console.log('Reset requested');
        })
        .catch(err => {
            console.error('Reset error:', err);
            alert('Failed to reset race. See console for details.');
        });
}
