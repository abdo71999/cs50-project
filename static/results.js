const dataElement = document.getElementById("regression-data");
const chartData = JSON.parse(dataElement.textContent);

const actualPoints = chartData.x.map((xValue, index) => ({
    x: xValue,
    y: chartData.actual[index]
}));

const predictedPoints = chartData.x.map((xValue, index) => ({
    x: xValue,
    y: chartData.predicted[index]
}));

const canvas = document.getElementById("regressionChart");

new Chart(canvas, {
    type: "scatter",
    data: {
        datasets: [
            {
                label: "Actual data",
                data: actualPoints,
                backgroundColor: "blue"
            },
            {
                label: "Fitted line",
                data: predictedPoints,
                showLine: true,
                pointRadius: 0,
                borderColor: "red",
                backgroundColor: "red"
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                type: "linear",
                title: {
                    display: true,
                    text: "X"
                }
            },
            y: {
                title: {
                    display: true,
                    text: "Y"
                }
            }
        }
    }
});