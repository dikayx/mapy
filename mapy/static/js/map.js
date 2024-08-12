/**
 * Initialize a Leaflet map with markers for each location in the locations array.
 */
document.addEventListener("DOMContentLoaded", function () {
    // Get the map element and its data attribute
    var mapElement = document.getElementById("map");
    var locations = JSON.parse(mapElement.getAttribute("data-locations"));

    // Check if the locations array is not empty
    if (locations.length > 0) {
        // Initialize the map centered around the first location or default coordinates
        var initialLocation = locations[0];

        var map = L.map("map").setView(
            [initialLocation.latitude, initialLocation.longitude],
            4
        );
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution:
                '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map);

        // Array to store all the latlng points
        var latlngs = [];

        // Add a marker for each location in the locations array
        locations.forEach(function (location) {
            L.marker([location.latitude, location.longitude])
                .addTo(map)
                .bindPopup(
                    `<b>IP: ${location.ip}</b><br>Lat: ${location.latitude}<br>Lon: ${location.longitude}`
                );

            // Push the coordinates to the latlngs array
            latlngs.push([location.latitude, location.longitude]);
        });

        // If there is more than one location, draw a line connecting them
        if (latlngs.length > 1) {
            var polyline = L.polyline(latlngs, { color: "blue" }).addTo(map);
            // Adjust the map's bounds to fit the polyline
            map.fitBounds(polyline.getBounds());
        }
    }
});
