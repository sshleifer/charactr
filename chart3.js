// Create the dc.js chart objects & link to div
var dataTable = dc.dataTable("#dc-table-graph");
var charsChart = dc.rowChart("#dc-chars-chart");
var hourChart = dc.barChart("#dc-hour-chart");
var dayOfWeekChart = dc.rowChart("#dc-dayweek-chart");
var sentChart = dc.pieChart("#dc-sent-chart");
var timeChart = dc.lineChart("#dc-time-chart");

var pctFormat = d3.format('%')


d3.csv("msg.csv", function (data) {
  var format = d3.time.format("%Y-%m-%d %H:%M:%S");
  
  data.forEach(function(d) { 
    d.msg_len = + d.msg_len;
    d.tstamp = format.parse(d.tstamp);
    d.is_sent = + d.is_sent;
    d.date =  new Date(d.tstamp.getFullYear(), d.tstamp.getMonth(), d.tstamp.getDate()); 
  });

  // Run the data through crossfilter and load our 'facts'
  var facts = crossfilter(data);
  var all = facts.groupAll();
  // for chars
  var chars = facts.dimension(function (d) {
    return d.cname;       // add the chars dimension
  });
  
  var charsGroupSum = chars.group()
    .reduceSum(function(d) { return d.msg_len;});	// sums 

  var filtChar = {
    all: function () {
        return charsGroupSum.top(10);
    }
  }

  // time chart
  var timeseries = facts.dimension(function(d) {
    return d.date;
  });

  var timeseriesGroup = timeseries.group()
    .reduceSum(function(d) { return d.msg_len; });

  //row chart Day of Week
  var dayOfWeek = facts.dimension(function (d) {
    switch (d.tstamp.getDay()) {
      case 0:
        return "0.sunday";
      case 1:
        return "1.monday";
      case 2:
        return "2.tuesday";
      case 3:
        return "3.wednesday";
      case 4:
        return "4.thursday";
      case 5:
        return "5.friday";
      case 6:
        return "6.saturday";
    }
  });
  var dayOfWeekGroup = dayOfWeek.group()
    .reduceSum(function(d) { return d.msg_len; });

  var hour = facts.dimension(function (d) {
    return d.tstamp.getHours();});
  var hourGroup = hour.group()
    .reduceSum(function(d) { return d.msg_len; });
  //debugger;


  //Pie Chart
  var sent = facts.dimension(function (d) {
    return d.is_sent ? "Sent" : "Rec.";
    });
  var sentGroup = sent.group().reduceSum(function (d) {return d.msg_len;});
  
  var timeDimension = facts.dimension(function (d) {return d.tstamp;});
  // Setup the charts

  // count all the facts
  dc.dataCount(".dc-data-count")
    .dimension(facts)
    .group(all);
    
  // Magnitide Bar Graph Counted
  charsChart.width(300)
    .height(300)
    .margins({top: 5, left: 10, right: 10, bottom: 20})
    .dimension(chars)
    .group(filtChar)
    .colors(d3.scale.category10())
    .label(function (d){
       return d.key;
    })
    .title(function(d){return d.value;})
    .elasticX(true)
    .xAxis().ticks(4);
  
  // time graph
  timeChart.width(1100)
    .height(150)
    .transitionDuration(500)
   // .mouseZoomable(true)
    .margins({top: 10, right: 10, bottom: 20, left: 40})
    .dimension(timeseries)
    .group(timeseriesGroup)
//    .brushOn(false)			// added for title
    .elasticY(true)
    .x(d3.time.scale()
      .domain(d3.extent(data, function(d) { return d.date; })))
    .xAxis();

  //row chart day of week
  dayOfWeekChart.width(200)
    .height(220)
    .margins({top: 5, left: 10, right: 10, bottom: 20})
    .dimension(dayOfWeek)
    .group(dayOfWeekGroup)
    .colors(d3.scale.category10())
    .label(function (d){
       return d.key.split(".")[1];
    })
    .title(function(d){return d.value;})
    .elasticX(true)
    .xAxis().ticks(4);
  
  hourChart.width(400)
    .height(300)
    .margins({top: 5, left: 40, right: 10, bottom: 20})
    .dimension(hour)
    .group(hourGroup)
    .x(d3.scale.linear().domain([0,23]))
    .colors(d3.scale.category20())
    .label(function (d){
      return d.key;})
    .title(function(d){return d.value;})
    .elasticY(true)
    .xAxis().ticks(4);


  // is_sent pie chart
  sentChart.width(250)
    .height(220)
    .radius(100)
    .innerRadius(30)
    .dimension(sent)
    .group(sentGroup)
    .colors(d3.scale.category10())
    .label(function(d){
      return d.data.key + " (" + Math.round((d.endAngle-d.startAngle)/Math.PI * 50) + '%)';
    });


  // Data Table 
  dataTable.width(960).height(800)
    .dimension(timeDimension)
	.group(function(d) { return ""
	 })
	.size(200)
    .columns([
      function(d) {return d.cname;}, 
      function(d) {return d.tstamp.toString().slice(0,15);},
      function(d) {return d.tstamp.toString().slice(16,25);},
      function(d) {return d.is_sent ? "Sent" : "Received";},
      function(d) { return d.text; },
      function(d) { return d.msg_len;}
    ])
    .sortBy(function(d){ return d.tstamp; })
    .order(d3.ascending);
  // Render the Charts
  dc.renderAll();
});
  
