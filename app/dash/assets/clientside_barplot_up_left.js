window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside_barplot_up_left: {
        make_barplot_up_left: function(filteredData, selectedData) {
            const triggered = dash_clientside.callback_context.triggered.map(t => t.prop_id);

            if (triggered.includes("bar-graph.selectedData")) {
                return window.dash_clientside.no_update;
            }

            if (!filteredData || !Array.isArray(filteredData)) {
                return window.dash_clientside.no_update;
            }

            const grouped = {};
            const counts = {};

            for (const row of filteredData) {
                const tipo = row.tipo;
                const valor = row.valor;

                if (!tipo || typeof valor !== "number") continue;

                if (!(tipo in grouped)) {
                    grouped[tipo] = 0;
                    counts[tipo] = 0;
                }

                grouped[tipo] += valor;
                counts[tipo] += 1;
            }

            const averages = Object.entries(grouped)
                .map(([tipo, total]) => ({
                    tipo: tipo,
                    valor: total / counts[tipo]
                }))
                .sort((a, b) => a.valor - b.valor);  // Ascending order

            if (averages.length === 0) {
                return window.dash_clientside.no_update;
            }

            const trace = {
                type: "bar",
                x: averages.map(d => d.valor),
                y: averages.map(d => d.tipo),
                orientation: "h",
                text: averages.map(d => d.valor.toFixed(2)),
                textposition: "auto"
            };

            const layout = {
                clickmode: "event+select",
                dragmode: "select",
                template: "plotly_white",
                margin: {l: 170, r: 0, t: 0, b: 40},
                xaxis: {title: "Valor Médio (R$)"}
            };

            return {data: [trace], layout: layout};
        }
    }
});
