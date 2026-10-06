We proudly provide professional property and yard maintenance services across a wide footprint in Central Alberta. Click on any town below to focus the interactive map.

## Interactive Coverage Map

<div class="map-container">
    <iframe
        id="map-frame"
        src="https://maps.google.com/maps?q=Castor,+AB&z=9&output=embed"
        width="100%"
        height="450"
        style="border:0;"
        allowfullscreen=""
        loading="lazy"
        referrerpolicy="no-referrer-when-downgrade">
    </iframe>
</div>

## Regions We Serve

Select a location below to focus the map:

<div class="map-btn-grid">
    <button class="map-btn active" data-town="Castor,+AB">Castor</button>
    <button class="map-btn" data-town="Stettler,+AB">Stettler</button>
    <button class="map-btn" data-town="Coronation,+AB">Coronation</button>
    <button class="map-btn" data-town="Consort,+AB">Consort</button>
    <button class="map-btn" data-town="Red+Deer,+AB">Red Deer</button>
    <button class="map-btn" data-town="Lacombe,+AB">Lacombe</button>
</div>

<div class="quote-box">
    <h3>Outside Our Standard Radius?</h3>
    <p>Our standard service area extends roughly three hours from Castor, Alberta. If your property falls outside this radius, we may still be able to accommodate you &mdash; please visit our <a href="/contact/">Contact Us</a> page to request a custom travel quote.</p>
</div>

### Property Types Covered

If your property falls within our service perimeter, we offer scheduled seasonal management for residential yards, larger acreage layouts, historical preservation sites, and commercial lots.

<style>
    .map-container {
        width: 100%;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        overflow: hidden;
        margin: 20px 0;
        background-color: var(--surface-color);
    }
    .map-container iframe {
        display: block;
        width: 100%;
        height: 450px;
        border: 0;
    }
    .map-btn-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 20px 0 30px 0;
    }
    .map-btn {
        background-color: var(--surface-color);
        border: 1px solid var(--border-color);
        color: var(--text-color);
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-family: inherit;
        cursor: pointer;
        transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
    }
    .map-btn:hover {
        border-color: var(--primary-color);
        color: var(--primary-color);
    }
    .map-btn.active {
        background-color: var(--primary-color);
        border-color: var(--primary-color);
        color: #ffffff;
    }
    @media (max-width: 600px) {
        .map-btn { padding: 6px 12px; font-size: 0.85rem; }
    }
</style>

<script>
    (function() {
        var frame = document.getElementById('map-frame');
        var buttons = document.querySelectorAll('.map-btn');
        if (!frame || buttons.length === 0) return;

        buttons.forEach(function(btn) {
            btn.addEventListener('click', function() {
                buttons.forEach(function(b) { b.classList.remove('active'); });
                btn.classList.add('active');
                var q = btn.getAttribute('data-town');
                frame.src = "https://maps.google.com/maps?q=" + q + "&z=9&output=embed";
            });
        });
    })();
</script>
