// TODO: Improve the code to make it more readable and maintainable

var ipAddressData = Array.from(document.getElementById("table").rows)
    .flatMap((row) => {
        // Regular expression for matching IP addresses
        const ipRegex =
            /(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)|(\b(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}\b)/g;

        // Extract text from lat and lng cells
        const fromRow = row.cells[1].innerText;
        const byRow = row.cells[2].innerText;

        // Extract IP addresses from lat and lng text
        const fromIPs = fromRow.match(ipRegex) || [];
        const byIPs = byRow.match(ipRegex) || [];

        // Extract hostname from the IP address field
        const hostname = row.cells[0].innerText;

        // Combine all IPs and create an array of objects with hostname and ip fields
        return [...fromIPs, ...byIPs].map((ip) => ({ hostname, ip }));
    })
    .filter((result) => result.ip); // Filter out any results without an IP address

// For every ip, get the geolocation data using ipapi.co. Wait for each request to finish before moving on to the next one.
// Then, create an array in a format like { lat: 37.7749, lng: -122.4194, ip: "123.123.123.123" }
var ipGeolocationData = [];
var promise = Promise.resolve();
ipAddressData.forEach((result) => {
    promise = promise.then(() =>
        fetch("https://ipapi.co/" + result.ip + "/json/")
            .then((response) => response.json())
            .then((data) => {
                ipGeolocationData.push({
                    lat: data.latitude,
                    lng: data.longitude,
                    ip: result.ip,
                });
            })
    );
});

// Remove all entries, that contain undefined lat or lng or both
ipGeolocationData = ipGeolocationData.filter((entry) => entry.lat && entry.lng);

console.log(ipGeolocationData);

document.addEventListener("DOMContentLoaded", function () {
    // Initialize the map centered around the first hop or default coordinates
    var map = L.map("map").setView([0, 0], 2); // [latitude, longitude], zoom level

    // Use OpenStreetMap tiles
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution:
            '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    // Create example data for the hops
    var exampleHops = [
        { lat: 37.7749, lng: -122.4194, ip: "123.123.123.123" },
        { lat: 34.0522, lng: -118.2437, ip: "123.123.123.123" },
        { lat: 40.7128, lng: -74.006, ip: "123.123.123.123" },
    ];

    // Add markers for each hop
    ipGeolocationData.forEach(function (hop, index) {
        if (hop.lat && hop.lng) {
            var marker = L.marker([hop.lat, hop.lng]).addTo(map);
            marker.bindPopup("<b>Hop " + (index + 1) + "</b><br>IP: " + hop.ip);
        }
    });

    // // If there are any hops, center the map on the first hop
    if (ipGeolocationData.length > 0) {
        var firstHop = exampleHops[0];
        map.setView([firstHop.lat, firstHop.lng], 4);
    }
});
