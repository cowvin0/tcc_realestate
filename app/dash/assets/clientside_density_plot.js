window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside_density: {
        make_density_plot: function(filteredData, selectedData) {
            const triggered = dash_clientside.callback_context.triggered.map(t => t.prop_id);

            if (triggered.includes("density-plot.selectedData")) {
                return dash_clientside.no_update;
            }

            if (!filteredData || !Array.isArray(filteredData)) {
                return dash_clientside.no_update;
            }

            const grouped = {};
            for (const row of filteredData) {
                if (!row.tipo || row.valor == null) continue;
                if (!(row.tipo in grouped)) {
                    grouped[row.tipo] = [];
                }
                grouped[row.tipo].push(row.valor);
            }

            const traces = [];
            const tipos = Object.keys(grouped);
            for (const tipo of tipos) {
                const values = grouped[tipo];
                if (values.length < 2) continue;

                const n = values.length;
                const mean = values.reduce((a, b) => a + b, 0) / n;
                const std = Math.sqrt(values.reduce((sum, v) => sum + (v - mean) ** 2, 0) / n);

                if (std === 0) continue;

                traces.push({
                    type: "histogram",
                    x: values,
                    name: tipo,
                    xbins: {
                        size: 10000
                    },
                    opacity: 0.5
                });
            }

            if (traces.length === 0) {
                return dash_clientside.no_update;
            }

            const layout = {
                barmode: "overlay",
                legend: {
                    orientation: "h",
                    yanchor: "top",
                    y: -0.2,
                    xanchor: "center",
                    x: 0.5
                },
                margin: {l: 45, r: 0, t: 0, b: 30},
                clickmode: "event+select",
                dragmode: "select",
                template: "plotly_white",
                yaxis: {tickformat: ".1e"}
            };

            return {data: traces, layout: layout};
        }
    }
});
