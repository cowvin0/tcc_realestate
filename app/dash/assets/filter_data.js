window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        filter_data: function (
            selectedData_bar_up_left,
            selectedData_bar_bottom_right,
            selectedData_density,
            map_type,
            selectedData_map,
            filtered_data_all
        ) {
            const ctx = dash_clientside.callback_context;
            const changed = ctx.triggered.map(t => t.prop_id);

            let filtered = filtered_data_all;

            if (changed.includes("bar-graph.selectedData")) {
                if (selectedData_bar_up_left && selectedData_bar_up_left.points) {
                    const selectedTypes = new Set(
                        selectedData_bar_up_left.points.map(p => p.y)
                    );
                    filtered = filtered.filter(row => selectedTypes.has(row.tipo));
                }
            } else if (changed.includes("bar-plot-most-expensive.selectedData")) {
                if (selectedData_bar_bottom_right && selectedData_bar_bottom_right.points) {
                    const selectedBairros = new Set(
                        selectedData_bar_bottom_right.points.map(p => p.y)
                    );
                    filtered = filtered.filter(row => selectedBairros.has(row.bairro));
                }
            } else if (changed.includes("density-plot.selectedData")) {
                if (selectedData_density && selectedData_density.points) {
                    const selectedValues = new Set(
                        selectedData_density.points.map(p => Math.round(p.x))
                    );

                    filtered = filtered.filter(row => {
                        const rowValor = Math.round(Number(row.valor));
                        return selectedValues.has(rowValor);
                    });
                }
            }
            else if (changed.some(c => c.includes("plotly-map-container")) && map_type === "markers") {
                const mapData = selectedData_map;
                if (mapData && mapData.points) {
                    const selectedCoords = new Set(
                        mapData.points.map(p => `${p.lat},${p.lon}`)
                    );
                    filtered = filtered.filter(
                        row => selectedCoords.has(`${row.latitude},${row.longitude}`)
                    );
                }
            }
            else if (changed.some(c => c.includes("plotly-map-container")) && map_type === "bairros") {
                const bairroData = selectedData_map;
                if (bairroData && bairroData.points) {
                    const selectedBairros = new Set(
                        bairroData.points.map(p => p.location)
                    );
                    filtered = filtered.filter(row => selectedBairros.has(row.bairro));
                }
            }
            return filtered;
        }
    }
});
