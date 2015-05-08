margin ={top: 20, right: 300, bottom: 50, left: 50}
width = parseInt(d3.select('body').style('width'), 10) - margin.left - margin.right
height = 500 - margin.top - margin.bottom
winheight = d3.select('body').style('height') #Doesnt work
console.log(winheight)
exp = .4
center = (width - margin.right)/2 + margin.left
xValue = (d) ->  #value accessor
  d.lensent
xScale = d3.scale.pow().exponent(exp).range([0, width]).nice() #value->pixels
xMap = (d) ->  #data value to display value
  xScale(xValue(d))
xAxis = d3.svg.axis().scale(xScale).orient('bottom')

yValue = (d) ->
  d.of_total
yScale = d3.scale.pow().exponent(exp).range([height,0]).nice()
yMap = (d) ->
  yScale(yValue(d))
yAxis = d3.svg.axis().scale(yScale).orient('left')

# add the graph canvas to the body of the webpage
svg = d3.select('body').append('svg')
  .attr('width': width + margin.left + margin.right,
  'height': height + margin.top + margin.bottom)
    .append('g')
  .attr('transform': 'translate(' + margin.left + ',' + margin.top + ')')

tooltip = d3.select('body').append('div').attr('class': 'tooltip')
tool2 = d3.select('body').append('div').attr('class':'tooltip')
  .style('opacity': 0,'border': 'solid', 'height': '90px')

d3.csv('ppl.csv', (error, data) ->
  sum = 0
  data.forEach (d) ->
    d.lensent = +d.lensent
    d.lenrec = +d.lenrec
    d.totlen = +d.totlen
    d.pct_sent = d.lensent/d.totlen
    sum = sum + d.totlen
    return
  data.forEach (d) ->
    d.of_total = d.totlen/sum
    return
  
  console.log('TotChars',sum)
  # don't want dots overlapping axis, so add in buffer to data domain
  xScale.domain [d3.min(data, xValue) - 1, d3.max(data, xValue) + 1]
  yScale.domain [d3.min(data, yValue) - 1, d3.max(data, yValue) + 1]

  svg.append("g")
    .attr("class", "xaxis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)
    .selectAll("text")
    .style("text-anchor", "end")
    .attr("dx", "-.8em")
    .attr("dy", ".15em")
    .attr("transform","rotate(-65)")

  svg.select("g").append('text')
    .attr('class': 'lab1','x': width,'y': -6)
    .attr("dy", ".15em")
    .attr('text-anchor':'end')
    .text('Characters Sent (Scale is exponential)')


  svg.append('g')
    .attr('class': 'yaxis').call(yAxis).append('text')
    .attr('class': 'lab2','transform': 'rotate(-90)','y': 6,'dy': '.71em')
    .style('text-anchor': 'end')
    .text('Characters Received')
  # draw dots
  svg.selectAll('.dot')
    .data(data).enter().append('circle')
   .attr('class': 'dot','r': 3,'cx': xMap,'cy':yMap)
   .style('opacity': .7,'fill': 'rgb(0,105,225)')
    .on 'mouseover', (d) ->
      tooltip.html('<b><u>' + d.cname + '</u>' +
        '<br/> sent: ' + d.lensent +
        '<br/> received: ' + d.lenrec +
        '<br/> total: ' + d.totlen +
        '<br/> first: ' + d.start +
        '<br/> last: ' + d.end + '</b>')
          .style('opacity':1,'left': d3.event.pageX + 5 + 'px','top': d3.event.pageY - 10 + 'px')
      #tool2.transition().duration(0)
      tool2.html('<b><u>' + d.cname + '</u>' +
        '<br/> sent: ' + d.lensent +
        '<br/> received: ' + d.lenrec +
        '<br/> total: ' + d.totlen +
        '<br/> first: ' + d.start +
        '<br/> last: ' + d.end + '</b>')
          .style('opacity':0,'left': margin.left + width / 2 + 'px', 'top': 500 + 'px')
      return
  console.log('new'+ width)

  console.log('center'+center)
  tabulate = (d1, columns) ->
    data = d1.sort( (a,b) ->
      b.totlen - a.totlen).slice(0,10)
    
    table = d3.select("body").append("table").style("margin-left": center+"px")
    thead = table.append("thead")
    tbody = table.append("tbody")
    thead.append("tr").selectAll("th")
      .data(columns).enter().append("th").text (column) ->
        column
    
    rows = tbody.selectAll("tr").data(data).enter().append("tr")

    cells = rows.selectAll('td').data((row) ->
      columns.map (column) ->
        {column: column, value:row[column]}
    ).enter().append("td").html( (d) ->
      d.value)

    return table

  peopleTable = tabulate(data, ["cname", "pct_sent", "totlen", "of_total"])
  return
)
        ##NEEDS TO BE SENT DATA SOMEHOW
addXax = (height, width)->

  d3.select('svg').select("g").selectAll(".xaxis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)
    .selectAll("text")
    .style("text-anchor", "end")
    .attr("dx", "-.8em")
    .attr("dy", ".15em")
    .attr("transform","rotate(-65)")

  d3.select('svg').select("g").select('.xaxis').select('.lab1')
    .attr('x': width)
    .attr("dy", ".15em")
    .attr('text-anchor':'end')
  return

re2 = -> # Find the new window dimensions */
  console.log('2. Resizing from width'+ width)
  width = parseInt(d3.select("body").style("width"),10) - margin.left - margin.right
  console.log ('2a. Resizing from width'+ width)
  height = parseInt(d3.select("body").style("height")) - margin.top - margin.bottom
  console.log ('2a. Resizing to height: '+ height)
  addXax(height,width)
  return

#d3.select(window).on('resize',re2)

console.log("all the points", xAxis.scale().ticks(xAxis.ticks()))
console.log('height',d3.select('body').style('height')) #Doesnt work
