(function () {

    const chart = document.getElementById(
        "dashboardCategoryChart"
    );

    if (!chart) {
        return;
    }

    const allSources = Array.from(
        chart.querySelectorAll(
            ".dashboard-category-source"
        )
    );

    function isHiddenCategory(name) {

        const normalized =
            String(name || "")
            .toLowerCase();

        return (
            normalized.includes(
                "μέσα ατομικής προστασίας"
            )
            || normalized.includes(
                "ατομικής προστασίας"
            )
            || normalized.includes(
                "μαπ"
            )
        );

    }

    const sources = allSources.filter(
        function (item) {
            return !isHiddenCategory(
                item.dataset.category
            );
        }
    );

    const svg = document.getElementById(
        "categoryPie"
    );

    const legend = document.getElementById(
        "categoryLegend"
    );

    const total = sources.reduce(
        (sum, item) =>
            sum + Number(
                item.dataset.count || 0
            ),
        0
    );

    if (!svg || !legend || !total) {
        return;
    }

    const SVG_NS =
        "http://www.w3.org/2000/svg";

    function svgEl(
        tag,
        attrs = {}
    ) {

        const el =
            document.createElementNS(
                SVG_NS,
                tag
            );

        Object.entries(attrs).forEach(
            ([key, value]) => {
                el.setAttribute(
                    key,
                    value
                );
            }
        );

        return el;

    }

    function colorFor(name) {

        const normalized =
            String(name || "")
            .toLowerCase();

        if (
            normalized.includes(
                "περιβαλλον"
            )
        ) {
            return "#2fa66f";
        }

        if (
            normalized.includes(
                "ηλεκτρ"
            )
        ) {
            return "#2878c8";
        }

        if (
            normalized.includes(
                "βοηθητικ"
            )
            || normalized.includes(
                "εργαλ"
            )
            || normalized.includes(
                "αναλώσι"
            )
        ) {
            return "#e781a8";
        }

        return "#8fb9d8";

    }

    function displayName(name) {

        const normalized =
            String(name || "")
            .toLowerCase();

        if (
            normalized.includes(
                "βοηθητικ"
            )
            || normalized.includes(
                "εργαλ"
            )
            || normalized.includes(
                "αναλώσι"
            )
        ) {
            return "Βοηθητικός Εξοπλισμός - Εργαλεία";
        }

        return name;

    }

    function shade(
        hex,
        amount
    ) {

        const num =
            parseInt(
                hex.replace("#", ""),
                16
            );

        const r = Math.max(
            0,
            Math.min(
                255,
                (num >> 16) + amount
            )
        );

        const g = Math.max(
            0,
            Math.min(
                255,
                ((num >> 8) & 255)
                + amount
            )
        );

        const b = Math.max(
            0,
            Math.min(
                255,
                (num & 255)
                + amount
            )
        );

        return (
            "#"
            + (
                0x1000000
                + (r << 16)
                + (g << 8)
                + b
            )
            .toString(16)
            .slice(1)
        );

    }

    function polar(
        cx,
        cy,
        radius,
        angle
    ) {

        const rad =
            (angle - 90)
            * Math.PI
            / 180;

        return {
            x:
                cx
                + radius
                * Math.cos(rad),
            y:
                cy
                + radius
                * 0.74
                * Math.sin(rad)
        };

    }

    function donutPath(
        cx,
        cy,
        outerRadius,
        innerRadius,
        startAngle,
        endAngle
    ) {

        const outerStart =
            polar(
                cx,
                cy,
                outerRadius,
                endAngle
            );

        const outerEnd =
            polar(
                cx,
                cy,
                outerRadius,
                startAngle
            );

        const innerStart =
            polar(
                cx,
                cy,
                innerRadius,
                startAngle
            );

        const innerEnd =
            polar(
                cx,
                cy,
                innerRadius,
                endAngle
            );

        const large =
            endAngle - startAngle > 180
                ? 1
                : 0;

        return [
            "M",
            outerStart.x,
            outerStart.y,
            "A",
            outerRadius,
            outerRadius * 0.74,
            0,
            large,
            0,
            outerEnd.x,
            outerEnd.y,
            "L",
            innerStart.x,
            innerStart.y,
            "A",
            innerRadius,
            innerRadius * 0.74,
            0,
            large,
            1,
            innerEnd.x,
            innerEnd.y,
            "Z"
        ].join(" ");

    }

    svg.innerHTML = "";

    const defs =
        svgEl("defs");

    const filter =
        svgEl(
            "filter",
            {
                id: "donutShadow",
                x: "-30%",
                y: "-30%",
                width: "160%",
                height: "180%"
            }
        );

    filter.appendChild(
        svgEl(
            "feDropShadow",
            {
                dx: "0",
                dy: "9",
                stdDeviation: "7",
                "flood-color": "#10263b",
                "flood-opacity": "0.22"
            }
        )
    );

    defs.appendChild(filter);
    svg.appendChild(defs);

    svg.appendChild(
        svgEl(
            "ellipse",
            {
                cx: "180",
                cy: "228",
                rx: "112",
                ry: "20",
                fill: "#17324b",
                opacity: "0.08"
            }
        )
    );

    let angle = -5;

    sources.forEach(
        function (
            item,
            index
        ) {

            const name =
                item.dataset.category;

            const count =
                Number(
                    item.dataset.count || 0
                );

            const sweep =
                (count / total)
                * 360;

            const startAngle =
                angle;

            const endAngle =
                angle + sweep;

            const midAngle =
                startAngle
                + sweep / 2;

            const baseColor =
                colorFor(name);

            const gradient =
                svgEl(
                    "linearGradient",
                    {
                        id:
                            "donutGradient"
                            + index,
                        x1: "0%",
                        y1: "0%",
                        x2: "100%",
                        y2: "100%"
                    }
                );

            [
                [
                    "0%",
                    "#ffffff",
                    "0.58"
                ],
                [
                    "18%",
                    shade(
                        baseColor,
                        45
                    ),
                    "0.94"
                ],
                [
                    "58%",
                    baseColor,
                    "0.88"
                ],
                [
                    "100%",
                    shade(
                        baseColor,
                        -36
                    ),
                    "0.94"
                ]
            ].forEach(
                function (stop) {

                    gradient.appendChild(
                        svgEl(
                            "stop",
                            {
                                offset:
                                    stop[0],
                                "stop-color":
                                    stop[1],
                                "stop-opacity":
                                    stop[2]
                            }
                        )
                    );

                }
            );

            defs.appendChild(
                gradient
            );

            const offsetRad =
                (midAngle - 90)
                * Math.PI
                / 180;

            const exploded =
                11;

            const cx =
                180
                + Math.cos(
                    offsetRad
                )
                * exploded;

            const cy =
                122
                + Math.sin(
                    offsetRad
                )
                * exploded
                * 0.74;

            const depth =
                18;

            const group =
                svgEl(
                    "g",
                    {
                        class:
                            "dashboard-donut-slice"
                    }
                );

            group.appendChild(
                svgEl(
                    "path",
                    {
                        d:
                            donutPath(
                                cx,
                                cy + depth,
                                103,
                                55,
                                startAngle,
                                endAngle
                            ),
                        fill:
                            shade(
                                baseColor,
                                -48
                            ),
                        opacity:
                            "0.88"
                    }
                )
            );

            group.appendChild(
                svgEl(
                    "path",
                    {
                        d:
                            donutPath(
                                cx,
                                cy,
                                103,
                                55,
                                startAngle,
                                endAngle
                            ),
                        fill:
                            "url(#donutGradient"
                            + index
                            + ")",
                        stroke:
                            "rgba(255,255,255,0.82)",
                        "stroke-width":
                            "2.3",
                        filter:
                            "url(#donutShadow)"
                    }
                )
            );

            svg.appendChild(
                group
            );


            const row =
                document.createElement(
                    "div"
                );

            row.className =
                "dashboard-category-legend-row";

            const dot =
                document.createElement(
                    "span"
                );

            dot.className =
                "dashboard-category-dot";

            dot.style.background =
                baseColor;

            const label =
                document.createElement(
                    "span"
                );

            label.className =
                "dashboard-category-name";

            label.textContent =
                displayName(name);

            const value =
                document.createElement(
                    "strong"
                );

            value.className =
                "dashboard-category-value";

            value.textContent =
                count;

            row.appendChild(dot);
            row.appendChild(label);
            row.appendChild(value);

            legend.appendChild(row);

            angle = endAngle;

        }
    );

})();



/* ======================= Interactive Mission Map ======================= */
(function () {
    const dataRoot = document.getElementById("missionMapData");
    const svg = document.getElementById("missionMapSvg");
    const routesLayer = document.getElementById("missionRoutesLayer");
    const stationsLayer = document.getElementById("missionStationsLayer");
    const info = document.getElementById("missionMapInfo");
    if (!dataRoot || !svg || !routesLayer || !stationsLayer || !info) return;

    const NS = "http://www.w3.org/2000/svg";
    /*
       Geographic coordinates -> the supplied isometric Greece reference.
       The coefficients are an affine calibration using mainland, Peloponnese,
       Crete, Rhodes and northern-Greece control points.
       This keeps real latitude/longitude data while matching the 3D perspective.
    */
    function project(lat, lon) {
        /*
           v1.41:
           1) Project WGS84 lat/lon into the GIS-correct source map.
           2) Apply the calibrated inverse homography that aligns the GIS
              geometry with the approved black/white reference design.
           No PNG coordinates or hand-written station offsets are used.
        */
        const WEST = 19.25, EAST = 28.55, SOUTH = 34.65, NORTH = 41.95;
        const COS0 = 0.784776370533;
        const SCALE = 139.178082191781;
        const PAD = 42;

        // GIS source map is 1100x1100; registration was solved on 1254x1254.
        const sourceScale = 1254 / 1100;
        const sx = (PAD + (lon - WEST) * COS0 * SCALE) * sourceScale;
        const sy = (PAD + (NORTH - lat) * SCALE) * sourceScale;

        // inverse(ECC homography): GIS source -> approved visual map
        const h11 = 1.04812233, h12 = -0.00789051, h13 = -72.89699218;
        const h21 = -0.00498172, h22 = 1.07200725, h23 = -58.78876166;
        const h31 = -0.00002211, h32 = -0.00000361, h33 = 1.00175850;

        const den = h31 * sx + h32 * sy + h33;
        let x = (h11 * sx + h12 * sy + h13) / den;
        let y = (h21 * sx + h22 * sy + h23) / den;

        return snapMapPointToLand({ x, y });
    }


    const mapVectorPaths = [...document.querySelectorAll("#missionMapVectorLayer .mission-map-vector-region")];

    function pointIsOnMapLand(x, y) {
        if (!window.DOMPoint || !mapVectorPaths.length) return true;
        const pt = new DOMPoint(x, y);
        return mapVectorPaths.some(path => {
            try { return path.isPointInFill(pt); } catch (_) { return false; }
        });
    }

    function snapMapPointToLand(point) {
        if (pointIsOnMapLand(point.x, point.y)) return point;

        /*
           Coastal facilities can lie directly on an antialiased/coastline edge.
           Search only a small radius so the geographic position is preserved.
        */
        const maxRadius = 18;
        for (let radius = 2; radius <= maxRadius; radius += 2) {
            for (let step = 0; step < 24; step++) {
                const angle = (Math.PI * 2 * step) / 24;
                const x = point.x + Math.cos(angle) * radius;
                const y = point.y + Math.sin(angle) * radius;
                if (pointIsOnMapLand(x, y)) return { x, y };
            }
        }
        return point;
    }

    function el(tag, attrs) {
        const node = document.createElementNS(NS, tag);
        Object.keys(attrs || {}).forEach(k => node.setAttribute(k, attrs[k]));
        return node;
    }

    const hq = {
        name: dataRoot.dataset.hqName || "Έδρα",
        address: dataRoot.dataset.hqAddress || "",
        lat: Number(dataRoot.dataset.hqLat),
        lon: Number(dataRoot.dataset.hqLon)
    };

    const stations = [...dataRoot.querySelectorAll(".mission-map-station-data")].map(n => ({
        id:n.dataset.id, code:n.dataset.code, name:n.dataset.name,
        category:n.dataset.category, energy:n.dataset.energy, area:n.dataset.area,
        address:n.dataset.address, accuracy:n.dataset.accuracy, status:n.dataset.status,
        verified:n.dataset.verified === "1",
        lat:Number(n.dataset.lat), lon:Number(n.dataset.lon),
        active:n.dataset.active === "1"
    })).filter(s => Number.isFinite(s.lat) && Number.isFinite(s.lon));

    const missions = [...dataRoot.querySelectorAll(".mission-map-mission-data")].map(n => ({
        id:n.dataset.id, code:n.dataset.code, destination:n.dataset.destination,
        team:n.dataset.team, departure:n.dataset.departure, vehicle:n.dataset.vehicle,
        plate:n.dataset.plate, count:n.dataset.count,
        lat:Number(n.dataset.lat), lon:Number(n.dataset.lon)
    })).filter(m => Number.isFinite(m.lat) && Number.isFinite(m.lon));

    function escapeHtml(value) {
        return String(value || "").replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
    }

    function showStation(station) {
        const activeHere = missions.filter(m => Math.abs(m.lat-station.lat)<0.01 && Math.abs(m.lon-station.lon)<0.01);
        info.innerHTML = `
            <div class="mission-map-info-card">
                <span class="mission-map-info-kicker">${station.code ? escapeHtml(station.code) + " · " : ""}${escapeHtml(station.category || "ΣΤΑΘΜΟΣ")}</span>
                <h3>${escapeHtml(station.name)}</h3>
                <p>${escapeHtml(station.area || station.address || "Χωρίς καταχωρισμένη περιοχή")}</p>
                ${station.energy ? `<div class="mission-map-station-meta"><span>Πηγή Ενέργειας</span><strong>${escapeHtml(station.energy)}</strong></div>` : ""}
                ${station.status ? `<div class="mission-map-station-meta"><span>Κατάσταση</span><strong>${escapeHtml(station.status)}</strong></div>` : ""}
                <div class="mission-map-coordinates">${station.lat.toFixed(5)}, ${station.lon.toFixed(5)}</div>
                ${station.accuracy ? `<p class="mission-map-accuracy">${escapeHtml(station.accuracy)}</p>` : ""}
                <div class="mission-map-verification ${station.verified ? "verified" : "provisional"}">
                    ${station.verified ? "✓ Επαληθευμένη Θέση" : "Υπό επαλήθευση"}
                </div>
                <div class="mission-map-info-stat"><span>Ενεργές αποστολές</span><strong>${activeHere.length}</strong></div>
            </div>`;
    }

    function showMission(mission) {
        info.innerHTML = `
            <div class="mission-map-info-card mission-map-active-card">
                <span class="mission-map-info-kicker">ΕΝΕΡΓΗ ΑΠΟΣΤΟΛΗ</span>
                <h3>${escapeHtml(mission.destination)}</h3>
                <div class="mission-map-detail-grid">
                    <span>Κωδικός</span><strong>${escapeHtml(mission.code)}</strong>
                    <span>Ομάδα</span><strong>${escapeHtml(mission.team)}</strong>
                    <span>Αναχώρηση</span><strong>${escapeHtml(mission.departure)}</strong>
                    <span>Όχημα</span><strong>${escapeHtml(mission.vehicle || "—")}</strong>
                    <span>Πινακίδα</span><strong>${escapeHtml(mission.plate || "—")}</strong>
                    <span>Εξοπλισμός</span><strong>${escapeHtml(mission.count)} τεμ.</strong>
                </div>
                <a class="primary-button mission-map-open-button" href="/missions/${encodeURIComponent(mission.id)}">Προβολή Αποστολής →</a>
            </div>`;
    }

    if (Number.isFinite(hq.lat) && Number.isFinite(hq.lon)) {
        const hp = project(hq.lat, hq.lon);
        const pulse = el("circle", { cx:hp.x, cy:hp.y, r:18, class:"mission-map-hq-pulse" });
        const dot = el("circle", { cx:hp.x, cy:hp.y, r:8, class:"mission-map-hq-dot" });
        stationsLayer.appendChild(pulse); stationsLayer.appendChild(dot);
        const label = el("text", { x:hp.x+14, y:hp.y-12, class:"mission-map-label mission-map-hq-label" });
        label.textContent = hq.name; stationsLayer.appendChild(label);
    }

    stations.forEach(station => {
        const p = project(station.lat, station.lon);
        const hasMission = missions.some(m => Math.abs(m.lat-station.lat)<0.01 && Math.abs(m.lon-station.lon)<0.01);
        const g = el("g", { class:"mission-map-clickable", tabindex:"0", role:"button", "aria-label":station.name });

        const normalizedCategory = (station.category || "").trim().toUpperCase();
        const normalizedEnergy = (station.energy || "").trim().toLowerCase();

        let stationTypeClass = "mission-map-station-other";

        if (
            normalizedCategory === "ΑΗΣ" &&
            normalizedEnergy.includes("φυσικό αέριο")
        ) {
            stationTypeClass = "mission-map-station-gas";
        } else if (normalizedCategory === "ΥΗΣ") {
            stationTypeClass = "mission-map-station-hydro";
        }

        const markerClass = hasMission
            ? `mission-map-active-station ${stationTypeClass}`
            : `mission-map-station-dot ${stationTypeClass}`;

        g.appendChild(
            el("circle", {
                cx:p.x,
                cy:p.y,
                r:hasMission ? 9 : 6,
                class:markerClass
            })
        );
        const label = el("text", { x:p.x+12, y:p.y+4, class:"mission-map-label" }); label.textContent=station.name; g.appendChild(label);
        g.addEventListener("click", () => showStation(station));
        g.addEventListener("keydown", e => { if(e.key==="Enter"||e.key===" "){e.preventDefault();showStation(station);} });
        stationsLayer.appendChild(g);
    });

    if (Number.isFinite(hq.lat) && Number.isFinite(hq.lon)) {
        const hp = project(hq.lat, hq.lon);
        missions.forEach((mission, index) => {
            const dp = project(mission.lat, mission.lon);
            const mx=(hp.x+dp.x)/2, my=(hp.y+dp.y)/2 - (48 + (index%3)*18);
            const path = el("path", {
                d:`M ${hp.x} ${hp.y} Q ${mx} ${my} ${dp.x} ${dp.y}`,
                class:"mission-map-route", "marker-end":"url(#missionArrow)", filter:"url(#routeGlow)", tabindex:"0", role:"button"
            });
            path.addEventListener("click", () => showMission(mission));
            path.addEventListener("keydown", e => { if(e.key==="Enter"||e.key===" "){e.preventDefault();showMission(mission);} });
            routesLayer.appendChild(path);
        });
    }

    /* -------- Mouse-wheel zoom + pointer drag pan -------- */
    const resetZoomButton = document.getElementById("missionMapResetZoom");

    const initialViewBox = svg.viewBox.baseVal;
    const BASE_X = initialViewBox.x;
    const BASE_Y = initialViewBox.y;
    const BASE_W = initialViewBox.width;
    const BASE_H = initialViewBox.height;

    /* Allow 45% extra zoom-out so the complete territory, including Crete and southern islands, always fits. */
    const MAX_OUT_FACTOR = 1.45;
    const MAX_VIEW_W = BASE_W * MAX_OUT_FACTOR;
    const MAX_VIEW_H = BASE_H * MAX_OUT_FACTOR;

    let viewW = MAX_VIEW_W;
    let viewH = MAX_VIEW_H;
    let viewX = BASE_X - (viewW - BASE_W) / 2;
    let viewY = BASE_Y - (viewH - BASE_H) / 2;

    let dragging = false;
    let lastClientX = 0, lastClientY = 0;

    function applyViewBox() {
        svg.setAttribute("viewBox", `${viewX} ${viewY} ${viewW} ${viewH}`);
    }

    function clampView() {
        viewW = Math.max(BASE_W / 5, Math.min(MAX_VIEW_W, viewW));
        viewH = Math.max(BASE_H / 5, Math.min(MAX_VIEW_H, viewH));

        const minX = BASE_X - (MAX_VIEW_W - BASE_W) / 2;
        const minY = BASE_Y - (MAX_VIEW_H - BASE_H) / 2;
        const maxX = BASE_X + BASE_W - viewW + (MAX_VIEW_W - BASE_W) / 2;
        const maxY = BASE_Y + BASE_H - viewH + (MAX_VIEW_H - BASE_H) / 2;

        viewX = Math.max(minX, Math.min(maxX, viewX));
        viewY = Math.max(minY, Math.min(maxY, viewY));
    }

    svg.addEventListener("wheel", (event) => {
        event.preventDefault();

        const rect = svg.getBoundingClientRect();
        const pointerX = viewX + ((event.clientX - rect.left) / rect.width) * viewW;
        const pointerY = viewY + ((event.clientY - rect.top) / rect.height) * viewH;

        const zoomFactor = event.deltaY < 0 ? 0.86 : 1.16;
        const nextW = viewW * zoomFactor;
        const nextH = viewH * zoomFactor;

        const ratioX = (pointerX - viewX) / viewW;
        const ratioY = (pointerY - viewY) / viewH;

        viewW = nextW;
        viewH = nextH;
        viewX = pointerX - ratioX * viewW;
        viewY = pointerY - ratioY * viewH;

        clampView();
        applyViewBox();
    }, { passive:false });

    svg.addEventListener("pointerdown", (event) => {
        if (event.button !== 0) return;
        dragging = true;
        lastClientX = event.clientX;
        lastClientY = event.clientY;
        svg.setPointerCapture(event.pointerId);
        svg.classList.add("is-panning");
    });

    svg.addEventListener("pointermove", (event) => {
        if (!dragging) return;
        const rect = svg.getBoundingClientRect();
        const dx = (event.clientX - lastClientX) / rect.width * viewW;
        const dy = (event.clientY - lastClientY) / rect.height * viewH;
        viewX -= dx;
        viewY -= dy;
        lastClientX = event.clientX;
        lastClientY = event.clientY;
        clampView();
        applyViewBox();
    });

    function stopPan(event) {
        dragging = false;
        svg.classList.remove("is-panning");
        if (event && svg.hasPointerCapture && svg.hasPointerCapture(event.pointerId)) {
            svg.releasePointerCapture(event.pointerId);
        }
    }

    svg.addEventListener("pointerup", stopPan);
    svg.addEventListener("pointercancel", stopPan);

    if (resetZoomButton) {
        resetZoomButton.addEventListener("click", () => {
            viewW = MAX_VIEW_W;
            viewH = MAX_VIEW_H;
            viewX = BASE_X - (viewW - BASE_W) / 2;
            viewY = BASE_Y - (viewH - BASE_H) / 2;
            applyViewBox();
        });
    }

    /* Start zoomed-out enough to show the whole Greek territory. */
    applyViewBox();
})();
