// Create the dc.js chart objects & link to div
var dataTable = dc.dataTable("#dc-table-graph");
var charsChart = dc.rowChart("#dc-chars-chart");
//var depthChart = dc.barChart("#dc-depth-chart");
var dayOfWeekChart = dc.rowChart("#dc-dayweek-chart");
var islandChart = dc.pieChart("#dc-sent-chart");
var timeChart = dc.lineChart("#dc-time-chart");

// load data from a csv file
d3.csv("msg.csv", function (data) {
  var format = d3.time.format("%Y-%m-%d %H:%M:%S");
  //filter data? 
  data.forEach(function(d) { 
    d.msg_len = + d.msg_len;
    d.tstamp = format.parse(d.tstamp);
    d.is_sent = + d.is_sent;
    d.hour = d.tstamp.getHours(); 
    d.month = d.tstamp.getMonth();
    d.day = d.tstamp.getDate();
    d.year = d.tstamp.getFullYear();
    d.date =  new Date(d.year, d.month, d.day); 
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

  //  debugger;
  var top10 = charsGroupSum.top(10) 
  var besties = new Array();
  for (i = 0; i< 10; i++){
	  besties.push(top10[i].key);
  }
  var isBesty = function (name){
    return (besties.indexOf(name) == -1) ? 0 : 1;
  };
  
  var filtChar = {
    all: function () {
        return charsGroupSum.top(Infinity).filter( function (d) { return isBesty(d.key);} );
    }
}

  //debugger;
  // time chart
  var volumebyMonth = facts.dimension(function(d) {
    return d.date;
  });

  var volumebyMonthGroup = volumebyMonth.group()
    .reduceSum(function(d) { return d.msg_len; });

  //debugger;
  //row chart Day of Week
  var dayOfWeek = facts.dimension(function (d) {
    switch (d.tstamp.getDay()) {
      case 0:
        return "0.Sun";
      case 1:
        return "1.Mon";
      case 2:
        return "2.Tue";
      case 3:
        return "3.Wed";
      case 4:
        return "4.Thu";
      case 5:
        return "5.Fri";
      case 6:
        return "6.Sat";
    }
  });
  var dayOfWeekGroup = dayOfWeek.group()
    .reduceSum(function(d) { return d.msg_len; });


  //Pie Chart
  var sent = facts.dimension(function (d) {
    return d.is_sent ? "Sent" : "Received";
    });


  var sentGroup = sent.group().reduceSum(function (d) {return d.msg_len;});

  var timeDimension = facts.dimension(function (d) {return d.tstamp;});
  // Setup the charts

  // count all the facts
  dc.dataCount(".dc-data-count")
    .dimension(facts)
    .group(all);
    
  // Magnitide Bar Graph Counted
  charsChart.width(400)
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
  timeChart.width(960)
    .height(150)
    .transitionDuration(500)
   // .mouseZoomable(true)
    .margins({top: 10, right: 10, bottom: 20, left: 40})
    .dimension(volumebyMonth)
    .group(volumebyMonthGroup)
//    .brushOn(false)			// added for title
    .title(function(d){
      //return dtgFormat2(d.data.key)
      + "\nNumber of Events: " + d.value;
      })
	.elasticY(true)
    .x(d3.time.scale()
      .domain(d3.extent(data, function(d) { return d.date; })))
    .xAxis();

  //row chart day of week
  dayOfWeekChart.width(300)
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

  // is_sent pie chart
  islandChart.width(250)
    .height(220)
    .radius(100)
    .innerRadius(30)
    .dimension(sent)
    .title(function(d){return d.value;})
    .group(sentGroup);
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

      //function(d) {return d.tstamp;},
      function(d) {return d.is_sent ? "Sent" : "Received";},
      function(d) { return d.text; },
      function(d) { return d.msg_len;}
    ])
    .sortBy(function(d){ return d.tstamp; })
    .order(d3.ascending);
  // Render the Charts
  dc.renderAll();
});
  
