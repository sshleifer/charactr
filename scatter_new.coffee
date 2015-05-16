margin ={top: 20, right: 100, bottom: 50, left: 50}
tabwidth = 250
width = parseInt(d3.select('body').style('width'), 10) - margin.left - margin.right - tabwidth
height = 500 - margin.top - margin.bottom
exp = .4
center = (width - margin.right)/2 + margin.left
xValue = (d) ->  #value accessor
  d.lensent
xScale = d3.scale.pow().exponent(exp).range([0, width]).nice() #value->pixels
xMap = (d) ->  #data value to display value
  xScale(xValue(d))
xAxis = d3.svg.axis().scale(xScale).orient('bottom')

yValue = (d) ->
  d.lenrec
yScale = d3.scale.pow().exponent(exp).range([height,0]).nice()
yMap = (d) ->
  yScale(yValue(d))
yAxis = d3.svg.axis().scale(yScale).orient('left')

String.prototype.startsWith =  (str) ->
  return this.indexOf(str) == 0

dispatch = d3.dispatch("load", "statechange")

#div = d3.select("body").append("div")
#  .attr("class", "table")
#  .style("opacity", 0)

# add the graph canvas to the body of the webpage
svg = d3.select('.chart').insert('svg')
  .attr('width': width + margin.left + margin.right,
  'height': height + margin.top + margin.bottom)
    .append('g')
  .attr('transform': 'translate(' + margin.left + ',' + margin.top + ')')

tooltip = d3.select('body').append('div').attr('class': 'tooltip')
#tool2 = d3.select('body').append('div').attr('class':'tooltip').style('opacity': 0,'border': 'solid', 'height': '90px')

 
tabulate = (d1, columns) ->
  data = d1.sort( (a,b) ->
    b.totlen - a.totlen).slice(0,25)
  table = d3.select('.leaders').append("table").style("float":"right")
  
  thead = table.append("thead")
  tbody = table.append("tbody")
  
  colnames = {'cname':'name', 'pct_sent': 'pct_sent','totlen':'total','of_total':'of_total'}
  thead.append("tr").selectAll("th")
    .data(columns).enter().append("th").text (column) ->
      colnames[column]
  
  rows = tbody.selectAll("tr").data(data).enter().append("tr")
  cells = rows.selectAll('td').data((row) ->
    columns.map (column) ->
      {column: column, value:row[column]}
  ).enter().append("td").html( (d, i) ->
    if typeof(d.value) == 'string'
      return d.value.trim()
    else if d.value < 1
      return d3.round(100*d.value,2) + "%"
    else
      return d.value
  )
  return table


d3.csv('ppl.csv', ((error, data) ->
  #if error throw error
  byName = d3.map()
  sum = 0
  data.forEach (d) ->
    d.lensent = +d.lensent
    d.lenrec = +d.lenrec
    d.totlen = +d.totlen
    d.pct_sent = d.lensent / d.totlen
    sum = sum + d.totlen
    d.cname = d.cname.trim()
    byName.set(d.cname.trim(), d)
  
  data.forEach (d) ->
    d.of_total = d.totlen/sum
    
  console.log('TotChars',sum)
  dispatch.load(data)
  #dispatch.statechange("erica leh", data)

  peopleTable = tabulate(data, ["cname", "pct_sent", "totlen", "of_total",])

  )
)
dispatch.on("load.scatter", (data) ->
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
    .attr('id': ((d) -> return d.cname), 'class': 'dot','r': 3,'cx': xMap,'cy':yMap)
    .style('opacity': .7,'fill': 'rgb(0,105,225)')
    .on 'mouseover', (d) ->
      tooltip.html('<b><u>' + d.cname + '</u>' +
        '<br/> sent: ' + d.lensent +
        '<br/> received: ' + d.lenrec +
        '<br/> total: ' + d.totlen +
        '<br/> first: ' + d.start +
        '<br/> last: ' + d.end + '</b>')
          .style('opacity':1,'left': d3.event.pageX+5+'px','top': d3.event.pageY - 10 + 'px')
    .on('click', (d) -> d3.select(this).attr('r':3).style('fill':'rgb(0,105,225)'))
    
  dispatch.on("statechange.scatter", (selectValue, data) ->
    console.log('selecting', selectValue)
    console.log('take 2:', d3.select('select').property('value'))
    k = svg.selectAll(".dot").filter((data) ->
      return data.cname == selectValue).style("fill":"red").attr('r':10)
    
    console.log('tried to select', '#' + selectValue)
  )
)

dispatch.on("load.menu", (data) ->
  select = d3.select('.page')
    .append('div')
    .append('select')
      .attr('class':'select').style('fill': "red")

         
  select.selectAll('option')
    .data(data).enter().append('option')
    .attr("value": (d) -> d.cname)
    .text( (d) ->
      return d.cname)
        .style('color':'red')

  select.on('change',() -> dispatch.statechange(this.value, data))
)


addXax = (height, width)->
  xScale = d3.scale.pow().exponent(exp).range([0, width]).nice()
  xAxis = d3.svg.axis().scale(xScale).orient('bottom')

  d3.select('svg').select("g").select(".xaxis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)
    #.selectAll(".tick")

  d3.select('svg').select("g").select('.xaxis').select('.lab1')
    .attr('x': width)
    .attr("dy", ".15em")
  return

re2 = -> # Find the new window dimensions */
  console.log('2. Resizing from width'+ width)
  width = parseInt(d3.select("body").style("width"),10) - margin.left - margin.right
  console.log ('2a. Resizing from width'+ width)
  #height = parseInt(d3.select("body").style("height")) - margin.top - margin.bottom
  console.log ('2a. Resizing to height: '+ height)
  addXax(height,width)
  #d3.csv('ppl.csv',k)
  return
