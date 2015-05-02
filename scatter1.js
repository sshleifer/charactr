var margin = {top: 20, right: 200, bottom: 30, left: 50},
    width = parseInt(d3.select("#chart").style('width'), 10),
    width = width - margin.left - margin.right,
    winheight = parseInt(d3.select("#chart").style('height'), 10),
    height = 500 - margin.top - margin.bottom;

    //percent = d3.format('%');

var exp = .4;

/* 
 * value accessor - returns the value to encode for a given data object.
 * scale - maps value to a visual display encoding, such as a pixel position.
 * map function - maps from data value to display value
 * axis - sets up axis
 */ 

// setup x 
var xValue = function(d) { return d.lensent;}, // data -> value
    xScale = d3.scale.pow().exponent(exp).range([0, width]), // value -> display
    xMap = function(d) { return xScale(xValue(d));}, // data -> display
    xAxis = d3.svg.axis().scale(xScale).orient("bottom");

var startValue = function(d){return d.start;};
var endValue = function(d){return d.end;};

// setup y
var yValue = function(d) { return d.lenrec;}, // data -> value
    yScale = d3.scale.pow().exponent(exp).range([height, 0]), // value -> display
    yMap = function(d) { return yScale(yValue(d));}, // data -> display
    yAxis = d3.svg.axis().scale(yScale).orient("left");

// setup fill color
var cValue = function(d) { return d.cname;},
    color = "blue";

// add the graph canvas to the body of the webpage
var svg = d3.select("body").append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// add the tooltip area to the webpage
var tooltip = d3.select("body").append("div")
  .attr("class", "tooltip")
  .style("opacity", 0);

var tool2 = d3.select("body").append("div")
  .attr("class", "tooltip")
  .style("opacity", 0);


// load data
d3.csv("ppl.csv", function(error, data) {
  // change string (from CSV) into number format
  data.forEach(function(d) {
    d.lensent = +d.lensent;
    d.lenrec = +d.lenrec;
    console.log(d);
  });

  // don't want dots overlapping axis, so add in buffer to data domain
  xScale.domain([d3.min(data, xValue)-1, d3.max(data, xValue)+1]);
  yScale.domain([d3.min(data, yValue)-1, d3.max(data, yValue)+1]);
   // x-axis
  svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)
    .append("text")
    .attr("class", "label")
    .attr("x", width)
    .attr("y", -6)
    .style("text-anchor", "end")
    .text("Characters Sent (Scale is exponential)");

  // y-axis
  svg.append("g")
    .attr("class", "y axis")
    .call(yAxis)
    .append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", 6)
    .attr("dy", ".71em")
    .style("text-anchor", "end")
    .text("Characters Received");

  // draw dots
  svg.selectAll(".dot")
    .data(data)
    .enter().append("circle")
    .attr("class", "dot")
    .attr("r", 3)
    .attr("cx", xMap)
    .attr("cy", yMap)
    .style("opacity",.7)
    //.style("fill", function(d) { return color(cValue(d));}) 
    .style("fill", "rgb(0,105,225)") 
    .on("mouseover", function(d) {
      tooltip.transition()
        .duration(200)
        .style("opacity", 1);
      tooltip.html("<b><u>" + d.cname +"</u>" +
        "<br/> sent: " + xValue(d) +
        "<br/> received: " + yValue(d) + 
        "<br/> total: " + (xValue(d) + yValue(d)) +
        "<br/> first: " + startValue(d) + 
        "<br/> last: " + endValue(d) + "</b>")
        .style("left", (d3.event.pageX + 5) + "px")
        .style("top", (d3.event.pageY - 10) + "px");
      tool2.transition()
        .duration(200)
        .style("opacity", 1);
      tool2.html("<b><u>" + d.cname +"</u>" +
        "<br/> sent: " + xValue(d) +
        "<br/> received: " + yValue(d) + 
        "<br/> total: " + (xValue(d) + yValue(d)) +
        "<br/> first: " + startValue(d) + 
        "<br/> last: " + endValue(d) + "</b>")
        .style("left", (margin.left + width/2) + "px")
        .style("top", (500) + "px")
        .style("width", 500);
  //.style("background-color", "white"); 

    })
  /*.on("mouseout", function(d) {
    tooltip.transition()
      .duration(500)
      .style("opacity", 0);
  });*/


  
function resize() {
    console.log("Resizing from width", width)
    width =  parseInt(d3.select("#chart").style('width'), 10)
    width = width - margin.left - margin.right,
    xScale = d3.scale.pow().range([0, width]),
    xMap = function(d) { return xScale(xValue(d));}, // data -> display
    xAxis = d3.svg.axis().scale(xScale).orient("bottom");
}
 
d3.select(window).on('resize', resize); 


//draw legend

  /*
     var legend = svg.selectAll(".legend")
     .data(color.domain())
     .enter().append("g")
     .attr("class", "legend")
     .attr("transform", function(d, i) { return "translate(0," + i * 10 + ")"; });

  // draw legend colored rectangles
  legend.append("rect")
  .attr("x", width - 18)
  .attr("width", 18)
  .attr("height", 18)
  .style("fill", color);

  // draw legend text
  legend.append("text")
  .attr("x", width - 24)
  .attr("y", 9)
  .attr("dy", ".35em")
  .style("text-anchor", "end")
  .text(function(d) { return d;})
  */
}); 
