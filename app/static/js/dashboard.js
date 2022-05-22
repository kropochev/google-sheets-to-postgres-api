/* globals Chart:false, feather:false */

(function draw () {
  'use strict'

  feather.replace({ 'aria-hidden': 'true' })

  var delivery_time_data = document.getElementsByClassName('delivery_time')
  var price_usd_data = document.getElementsByClassName('price_usd')
  
  if (delivery_time_data.length === 0 || price_usd_data.length === 0) {
    return;
  }

  var labels = []
  var price = []

  var i;
  for (i = 0; i<delivery_time_data.length; i++) {
    labels.push(delivery_time_data[i].innerHTML);
    price.push(Number(price_usd_data[i].innerHTML));
  }
  const reducer = (accumulator, curr) => accumulator + curr;
  
  var total_price = document.getElementById('total_price');
  total_price.innerHTML = price.reduce(reducer);

  // Graphs
  var ctx = document.getElementById('myChart')
  // eslint-disable-next-line no-unused-vars
  var myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        data: price,
        lineTension: 0,
        backgroundColor: 'transparent',
        borderColor: '#007bff',
        borderWidth: 4,
        pointBackgroundColor: '#007bff'
      }]
    },
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: false
          }
        }]
      },
      legend: {
        display: false
      }
    }
  })
})()
