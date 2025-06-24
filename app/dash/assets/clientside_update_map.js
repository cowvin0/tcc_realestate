window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside_update_map: {
        update_map: function (
            map_type,
            filteredData,
            filteredDataAll,
            n_clicks,
            selected_,
            bairroGeojson,
            faixasExclusivasGeojson,
            cicloGeojson,
            comunidadesGeojson,
            corredoresGeojson,
            parquesGeojson,
            riosGeojson,
            pracasGeojson,
            escolasPublicasGeojson,
        ) {
            const triggered = dash_clientside.callback_context.triggered.map(t => t.prop_id);
            if (!filteredData || filteredData.length === 0) {
                return dash_clientside.no_update;
            }

            const plotlyContainer = document.getElementById('plotly-map-container');
            const leafletContainer = document.getElementById('leaflet-map-container');

            if (n_clicks % 2 === 1) {
                map_type = "sem_tipo";
            }

            if (window.myLeafletMap && map_type !== 'sem_tipo') {
                window.myLeafletMap.remove();
                window.myLeafletMap = null;
            }

            if (map_type === 'sem_tipo') {
                if (plotlyContainer) plotlyContainer.style.display = 'none';
                if (leafletContainer) leafletContainer.style.display = 'block';
            } else {
                if (plotlyContainer) plotlyContainer.style.display = 'block';
                if (leafletContainer) leafletContainer.style.display = 'none';
            }

            const CENTER_LAT = -7.1195;
            const CENTER_LON = -34.845;


            if (map_type === 'heatmap') {
                const latitudes = filteredData.map(row => row.latitude);
                const longitudes = filteredData.map(row => row.longitude);
                const values = filteredData.map(row => row.valor);

                var data = [{
                    'type': 'densitymapbox',
                    'lat': latitudes,
                    'lon': longitudes,
                    'z': values,
                    'radius': 13,
                    'colorscale': 'Viridis',
                    'showscale': true
                }];

                var layout = {
                    'mapbox': {
                        'style': 'open-street-map',
                        'center': { 'lat': CENTER_LAT, 'lon': CENTER_LON },
                        'zoom': 12
                    },
                    'margin': { 'r': 0, 't': 0, 'l': 0, 'b': 0 },
                };

                return [{ data: data, layout: layout }, "", "", "", "", "", {}];
            } else if (map_type === 'markers') {

                if (triggered.includes('plotly-map-container.selectedData')) {
                    return dash_clientside.no_update;
                }

                const latitudes = filteredData.map(row => row.latitude);
                const longitudes = filteredData.map(row => row.longitude);
                const values = filteredData.map(row => row.valor);
                const tipos = filteredData.map(row => row.tipo);

                const hoverText = filteredData.map(row =>
                    `Tipo: ${row.tipo}<br>Bairro: ${row.bairro}<br>Valor: R$ ${row.valor.toFixed(2)}<br>` +
                    `Área: ${row.area.toFixed(2)} m²<br>Vagas: ${row.vaga.toFixed(2)}<br>` +
                    `Banheiros: ${row.banheiro.toFixed(2)}<br>Quartos: ${row.quarto.toFixed(2)}<br>` +
                    `Predição: R$ ${row.predicoes_modelo.toFixed(2)}`
                );

                const sizes = values.map(v => Math.sqrt(v));

                const data = [{
                    type: 'scattermapbox',
                    lat: latitudes,
                    lon: longitudes,
                    mode: 'markers',
                    marker: {
                        size: sizes,
                        sizemode: 'area',
                        sizeref: 2.0 * Math.max(...sizes) / (15 ** 2),
                        sizemin: 4,
                        color: values,
                        colorscale: 'Viridis',
                        cmin: Math.min(...values),
                        cmax: Math.max(...values),
                        colorbar: {
                            title: 'Valor (R$)',
                            tickformat: '.2s',
                            titlefont: { size: 12 }
                        }
                    },
                    text: hoverText,
                    hoverinfo: 'text',
                }];

                const layout = {
                    mapbox: {
                        style: 'open-street-map',
                        center: { lat: CENTER_LAT, lon: CENTER_LON },
                        zoom: 12
                    },
                    margin: { 'r': 0, 't': 0, 'l': 0, 'b': 0 },
                    clickmode: 'event+select',
                    dragmode: 'select'
                };

                return [{ data: data, layout: layout }, "", "", "", "", "", {}];
            } else if (map_type === 'bairros') {

                if (triggered.includes('plotly-map-container.selectedData')) {
                    return dash_clientside.no_update;
                }

                const geojson = JSON.parse(bairroGeojson);
                const features = geojson.features;

                const valorMap = {};
                filteredData.forEach(row => {
                    if (!valorMap[row.bairro]) {
                        valorMap[row.bairro] = [];
                    }
                    valorMap[row.bairro].push(row.valor);
                });

                const locations = [];
                const z = [];
                features.forEach(feature => {
                    const nome = feature.properties.nome;
                    const valores = valorMap[nome];
                    if (valores) {
                        const avg = valores.reduce((a, b) => a + b, 0) / valores.length;
                        locations.push(nome);
                        z.push(avg);
                    }
                });

                const data = [{
                    type: 'choroplethmapbox',
                    geojson: geojson,
                    locations: locations,
                    z: z,
                    featureidkey: 'properties.nome',
                    colorscale: 'Viridis',
                    marker: {
                        line: { width: 0 }
                    },
                    zmin: Math.min(...z),
                    zmax: Math.max(...z),
                    colorbar: {
                        title: 'Valor (R$)',
                        tickformat: '.2s',
                        titlefont: { size: 12 }
                    },
                    hoverinfo: 'location+z',
                    opacity: 0.6
                }];

                const layout = {
                    mapbox: {
                        style: 'open-street-map',
                        center: { lat: CENTER_LAT, lon: CENTER_LON },
                        zoom: 12
                    },
                    margin: { 'r': 0, 't': 0, 'l': 0, 'b': 0 },
                    clickmode: 'event+select',
                    dragmode: 'select'
                };

                return [{ data: data, layout: layout }, "", "", "", "", "", {}];
            } else if (map_type === "faixas_exclusivas") {
                const geojson = JSON.parse(faixasExclusivasGeojson);

                const features = geojson.features.filter(f => f.geometry.type === "LineString");

                const lat = [];
                const lon = [];
                const hoverTexts = [];
                const lineGroups = [];

                features.forEach((feature, idx) => {
                    const coords = feature.geometry.coordinates;
                    const props = feature.properties;

                    const popupContent =
                        `<b>Ano de implantação:</b> ${props.ano_implantacao || "N/A"}<br>` +
                        `<b>Percurso:</b> ${props.percurso || "N/A"}`;

                    const lats = coords.map(c => c[1]);
                    const lons = coords.map(c => c[0]);

                    lat.push(lats);
                    lon.push(lons);
                    hoverTexts.push(popupContent);
                    lineGroups.push(idx);
                });

                const data = features.map((_, idx) => ({
                    type: 'scattermapbox',
                    mode: 'lines',
                    lat: lat[idx],
                    lon: lon[idx],
                    line: {
                        width: 3,
                        color: '#0074D9',
                    },
                    hoverinfo: 'text',
                    text: hoverTexts[idx],
                }));

                const layout = {
                    mapbox: {
                        style: 'open-street-map',
                        center: { lat: CENTER_LAT, lon: CENTER_LON },
                        zoom: 12,
                    },
                    margin: { t: 0, b: 0, l: 0, r: 0 },
                    hovermode: 'closest',
                    showlegend: false
                };

                return [{ data: data, layout: layout }, "", "", "", "", "", {}];
            } else if (map_type === "ciclo") {
                const geojson = JSON.parse(cicloGeojson);

                const features = geojson.features.filter(f => f.geometry.type === "LineString");

                const data = features.map((feature, idx) => {
                    const coords = feature.geometry.coordinates;
                    const props = feature.properties;

                    const lat = coords.map(c => c[1]);
                    const lon = coords.map(c => c[0]);

                    const ano = parseInt(props.ano_implantacao, 10) || "N/A";

                    const popupContent =
                        `<b>Tipo:</b> ${props.tipo || "N/A"}<br>` +
                        `<b>Sentido:</b> ${props.sentido || "N/A"}<br>` +
                        `<b>Ano de implantação:</b> ${ano}`;

                    return {
                        type: 'scattermapbox',
                        mode: 'lines',
                        lat: lat,
                        lon: lon,
                        line: {
                            width: 3,
                        },
                        hoverinfo: 'text',
                        text: popupContent
                    };
                });

                const layout = {
                    mapbox: {
                        style: 'open-street-map',
                        center: { lat: CENTER_LAT, lon: CENTER_LON },
                        zoom: 12,
                    },
                    margin: { t: 0, b: 0, l: 0, r: 0 },
                    hovermode: 'closest',
                    showlegend: false
                };

                return [{ data: data, layout: layout }, "", "", "", "", "", {}];
            }
            else if (map_type === "comunidades") {
                const geojson = JSON.parse(comunidadesGeojson);

                const data = geojson.features
                    .filter(f => f.geometry.type === "Polygon")
                    .map((feature, idx) => {
                        const coords = feature.geometry.coordinates[0];
                        const props = feature.properties;

                        const lat = coords.map(c => c[1]);
                        const lon = coords.map(c => c[0]);

                        const areaFormatted = parseFloat(props.area).toFixed(2);
                        const popupContent =
                            `<b>Comunidade:</b> ${props.comunidade || "N/A"}<br>` +
                            `<b>Área:</b> ${areaFormatted} m²`;

                        return {
                            type: 'scattermapbox',
                            mode: 'lines',
                            lat: [...lat, lat[0]],
                            lon: [...lon, lon[0]],
                            fill: 'toself',
                            line: {
                                width: 2
                            },
                            hoverinfo: 'text',
                            text: popupContent,
                            name: props.comunidade || `Área ${idx + 1}`
                        };
                    });

                const layout = {
                    mapbox: {
                        style: 'open-street-map',
                        center: { lat: CENTER_LAT, lon: CENTER_LON },
                        zoom: 12,
                    },
                    margin: { t: 0, b: 0, l: 0, r: 0 },
                    hovermode: 'closest',
                    showlegend: false
                };

                return [{ data: data, layout: layout }, "", "", "", "", "", {}];
            } else if (map_type === "corredores") {
                const geojson = JSON.parse(corredoresGeojson);

                const data = geojson.features
                    .filter(f => f.geometry.type === "LineString")
                    .map((feature, idx) => {
                        const coords = feature.geometry.coordinates;
                        const props = feature.properties;

                        const lat = coords.map(c => c[1]);
                        const lon = coords.map(c => c[0]);

                        const popupContent =
                            `<b>Corredor:</b> ${props.corredor || "N/A"}<br>` +
                            `<b>Descrição:</b> ${props.descricao || "N/A"}`;

                        return {
                            type: 'scattermapbox',
                            mode: 'lines',
                            lat: lat,
                            lon: lon,
                            line: {
                                width: 3
                            },
                            hoverinfo: 'text',
                            text: popupContent,
                            name: props.corredor || `Corredor ${idx + 1}`
                        };
                    });

                const layout = {
                    mapbox: {
                        style: 'open-street-map',
                        center: { lat: CENTER_LAT, lon: CENTER_LON },
                        zoom: 12,
                    },
                    margin: { t: 0, b: 0, l: 0, r: 0 },
                    hovermode: 'closest',
                    showlegend: false
                };

                return [{ data: data, layout: layout }, "", "", "", "", "", {}];
            } else if (map_type === "parques") {
                const geojson = JSON.parse(parquesGeojson);

                const data = geojson.features
                    .filter(f => f.geometry.type === "Polygon")
                    .map((feature, idx) => {
                        const coords = feature.geometry.coordinates[0];
                        const props = feature.properties;

                        const lat = coords.map(c => c[1]);
                        const lon = coords.map(c => c[0]);

                        if (lat[0] !== lat[lat.length - 1] || lon[0] !== lon[lon.length - 1]) {
                            lat.push(lat[0]);
                            lon.push(lon[0]);
                        }

                        const popupContent =
                            `<b>Nome:</b> ${props.nome || "N/A"}<br>` +
                            `<b>Perímetro:</b> ${Number(props.perimetro).toFixed(2)} m<br>` +
                            `<b>Área:</b> ${Number(props.area).toFixed(2)} m²<br>` +
                            `<b>Hectares:</b> ${Number(props.hectares).toFixed(2)} ha`;

                        return {
                            type: 'scattermapbox',
                            mode: 'lines',
                            lat: lat,
                            lon: lon,
                            line: {
                                width: 2
                            },
                            fill: 'toself',
                            hoverinfo: 'text',
                            text: popupContent,
                            name: props.nome || `Parque ${idx + 1}`
                        };
                    });

                const layout = {
                    mapbox: {
                        style: 'open-street-map',
                        center: { lat: CENTER_LAT, lon: CENTER_LON },
                        zoom: 12,
                    },
                    margin: { t: 0, b: 0, l: 0, r: 0 },
                    hovermode: 'closest',
                    showlegend: false
                };

                return [{ data: data, layout: layout }, "", "", "", "", "", {}];
            } else if (map_type === "escolas_publicas") {
                const geojson = JSON.parse(escolasPublicasGeojson);

                const latitudes = [];
                const longitudes = [];
                const texts = [];

                geojson.features.forEach((feature, idx) => {
                    const props = feature.properties;
                    const coords = feature.geometry.coordinates;

                    latitudes.push(coords[1]);
                    longitudes.push(coords[0]);

                    const popupContent = `
                        <b>Nome:</b> ${props.nome || "N/A"}<br>
                        <b>Categoria:</b> ${props.categoria || "N/A"}<br>
                        <b>Dependência:</b> ${props.dependencia || "N/A"}
                    `;

                    texts.push(popupContent);
                });

                const data = [{
                    type: 'scattermapbox',
                    mode: 'markers',
                    lat: latitudes,
                    lon: longitudes,
                    text: texts,
                    hoverinfo: 'text',
                    marker: {
                        size: 8,
                        opacity: 0.7
                    },
                    name: 'Escolas Públicas'
                }];

                const layout = {
                    mapbox: {
                        style: 'open-street-map',
                        center: { lat: CENTER_LAT, lon: CENTER_LON },
                        zoom: 12
                    },
                    margin: { t: 0, b: 0, l: 0, r: 0 },
                    hovermode: 'closest',
                    showlegend: false
                };

                return [{ data: data, layout: layout }, "", "", "", "", "", {}];
            } else if (map_type === "rios") {
                const geojson = JSON.parse(riosGeojson);
                const riverTraces = [];

                geojson.features.forEach((feature, idx) => {
                    const geometry = feature.geometry;
                    const props = feature.properties;

                    if (geometry.type === "LineString") {
                        const coords = geometry.coordinates;
                        const lats = coords.map(c => c[1]);
                        const lons = coords.map(c => c[0]);

                        const popupText = `
                            <b>Nome :</b> ${props.nome || "N/A"}<br>
                            <b>Tipo :</b> ${props.tipo || "N/A"}<br>
                            <b>Afluente :</b> ${props.afluente || "N/A"}<br>
                        `;

                        riverTraces.push({
                            type: 'scattermapbox',
                            mode: 'lines',
                            lat: lats,
                            lon: lons,
                            hoverinfo: 'text',
                            text: popupText,
                            line: {
                                width: 2,
                            },
                            name: props.nome || `Rio ${idx + 1}`
                        });
                    }
                });

                const layout = {
                    mapbox: {
                        style: 'open-street-map',
                        center: { lat: CENTER_LAT, lon: CENTER_LON },
                        zoom: 12
                    },
                    margin: { t: 0, b: 0, l: 0, r: 0 },
                    hovermode: 'closest',
                    showlegend: false
                };

                return [{ data: riverTraces, layout: layout }, "", "", "", "", "", {}];
            } else if (map_type === "pracas") {
                const geojson = JSON.parse(pracasGeojson);
                const traces = [];

                geojson.features.forEach((feature, idx) => {
                    const geometry = feature.geometry;
                    const props = feature.properties;

                    if (geometry.type === "Polygon") {
                        geometry.coordinates.forEach((ring, ringIdx) => {
                            const lats = ring.map(coord => coord[1]);
                            const lons = ring.map(coord => coord[0]);

                            let areaStr = (props.area || "").toString().replace(",", ".");
                            let areaFloat = parseFloat(areaStr);
                            let areaDisplay = isNaN(areaFloat) ? "N/A" : areaFloat.toFixed(2);

                            const popupText = `
                                <b>Bairro :</b> ${props.bairro || "N/A"}<br>
                                <b>Nome :</b> ${props.nome || "N/A"}<br>
                                <b>Área :</b> ${areaDisplay} m²<br>
                            `;

                            traces.push({
                                type: 'scattermapbox',
                                mode: 'lines',
                                lat: lats,
                                lon: lons,
                                fill: 'toself',
                                line: { width: 2, color: '#006400' },
                                text: popupText,
                                hoverinfo: 'text',
                                name: props.nome || `Praça ${idx + 1}`
                            });
                        });
                    }
                });

                const layout = {
                    mapbox: {
                        style: 'open-street-map',
                        center: { lat: CENTER_LAT, lon: CENTER_LON },
                        zoom: 12
                    },
                    margin: { t: 0, b: 0, l: 0, r: 0 },
                    hovermode: 'closest',
                    showlegend: false
                };

                return [{ data: traces, layout: layout }, "", "", "", "", "", {}];
            }
            else {
                if (window.myLeafletMap) {
                    window.myLeafletMap.remove();
                }

                let aluguel_price = null;
                let aluguel_area = null;
                let lat = null;
                let lon = null;

                const map = L.map("leaflet-map-container", {
                    center: [CENTER_LAT, CENTER_LON],
                    zoom: 12,
                    zoomControl: true,
                });

                L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                    attribution: '&copy; OpenStreetMap contributors'
                }).addTo(map);

                var clickMarker = null;

                let clickResolve;
                const clickPromise = new Promise((resolve) => {
                    clickResolve = resolve;
                });

                function onMapClick(e) {
                    lat = e.latlng.lat;
                    lon = e.latlng.lng;

                    const point = [lon, lat];

                    let matchedBairro = null;
                    for (let feature of JSON.parse(bairroGeojson).features) {
                        if (turf.booleanPointInPolygon(point, feature.geometry)) {
                            matchedBairro = feature.properties.nome;
                            break;
                        }
                    }

                    aluguel_price = null;
                    aluguel_area = null;

                    if (matchedBairro) {
                        const filtered = filteredDataAll.filter(
                            row => row.bairro === matchedBairro
                        );

                        if (filtered.length > 0) {
                            const last = filtered[filtered.length - 1];
                            aluguel_price = last.valor_aluguel || null;
                            aluguel_area = last.area_aluguel || null;
                        }
                    }

                    if (clickMarker) {
                        map.removeLayer(clickMarker);
                    }

                    clickMarker = L.circleMarker([lat, lon], {
                        radius: 8,
                        color: "red",
                        fillColor: "red",
                        fillOpacity: 0.8
                    }).addTo(map);

                    let popupContent =
                        `<b>Coordenadas:</b> ${lat.toFixed(6)}, ${lon.toFixed(6)}<br>` +
                        `<b>Bairro:</b> ${matchedBairro || "N/A"}<br>` +
                        `<b>Preço Aluguel:</b> ${aluguel_price !== null ? `R$ ${aluguel_price.toFixed(2)}` : "N/A"}<br>` +
                        `<b>Área Aluguel:</b> ${aluguel_area !== null ? `${aluguel_area.toFixed(2)} m²` : "N/A"}`;

                    window.areaAluguel = aluguel_price
                    window.valorAluguel = aluguel_area
                    window.coords = e.latlng


                    clickMarker.bindPopup(popupContent).openPopup();

                    clickResolve([
                        {},
                        aluguel_price !== null ? aluguel_price : "",
                        aluguel_area !== null ? aluguel_area : "",
                        lat !== null ? lat : "",
                        lon !== null ? lon : "",
                        e.latlng
                    ]);
                }


                map.on('click', onMapClick);

                window.myLeafletMap = map;

                return clickPromise;
            }
        }
    }
});
