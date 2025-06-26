window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside_barplot_bottom_right: {
        make_barplot_bottom_right: function(filteredData, selectedData) {
            const triggered = dash_clientside.callback_context.triggered.map(t => t.prop_id);

            if (triggered.includes("bar-plot-most-expensive.selectedData")) {
                return window.dash_clientside.no_update;
            }

            if (!filteredData || !Array.isArray(filteredData)) {
                return window.dash_clientside.no_update;
            }

            const grouped = {};
            const counts = {};

            for (const row of filteredData) {
                const bairro = row.bairro;
                const valor = row.valor;

                if (!bairro || typeof valor !== "number") continue;

                if (!(bairro in grouped)) {
                    grouped[bairro] = 0;
                    counts[bairro] = 0;
                }

                grouped[bairro] += valor;
                counts[bairro] += 1;
            }

            const averages = Object.entries(grouped)
                .map(([bairro, total]) => ({
                    bairro: bairro,
                    valor: total / counts[bairro]
                }))
                .sort((a, b) => b.valor - a.valor)
                .slice(0, 10)
                .sort((a, b) => a.valor - b.valor);

            if (averages.length === 0) {
                return window.dash_clientside.no_update;
            }

            const trace = {
                type: "bar",
                x: averages.map(d => d.valor),
                y: averages.map(d => d.bairro),
                orientation: "h",
                text: averages.map(d => d.valor.toFixed(2)),
                textposition: "auto"
            };

            const layout = {
                clickmode: "event+select",
                dragmode: "select",
                template: "plotly_white",
                margin: {l: 170, r: 0, t: 0, b: 40},
                yaxis: {tickformat: ".2f"},
                xaxis: {title: "Valor Médio (R$)"},
            };

            return {data: [trace], layout: layout};
        }
    }
});
