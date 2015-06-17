var fill = d3.scale.category20();

// takes in a string of words delimited by commas, returns an array of objects
// of type {text: string, size: int}
function processData (x) {
    var words = x.split(',');
    var counts = {};
    var total_count = 0;

    for (var i = 0; i < words.length; i++) {
      var cur = words[i];
      counts[cur] = counts[cur] ? counts[cur] + 1 : 1;
    }

    var words_arr = [];
    var i = 0;
    for (var prop in counts) {
        words_arr[i] = {text: prop, size: Math.pow(counts[prop], .65)};
        i = i + 1;
    }
    
    words_arr.sort(function(a, b) {
      return b.size - a.size;
    });

    for (var j = 1; j < 251; j++) {
        total_count += words_arr[j].size;
    }

    var multiplier = (130 * total_count) / words_arr[1].size;

    for (var j = 1; j < 251; j++) {
        words_arr[j].size = (multiplier * words_arr[j].size) / total_count;
    }

    return words_arr.slice(1, 250);
}

$(document).ready(function() {
  $.ajax({
    type: "GET",
    url: "word_cloud.txt",
    dataType: "text",
    success: function(data) {
      var counts = processData(data);//.substring(0, 10000000));
      // var angles = [-90, -60, -30, 0, 30, 60, 90];

      d3.layout.cloud().size([1200, 1000])
        .timeInterval(10)
        .words(counts) // [{text: "Sam", size: 60}, {text: "Peter", size: 70}])
        .padding(5)
        .rotate(function() { 
                  angle = 0 //~~(Math.random() * 2) * 90;
                  // angle = angles[~~(Math.random() * 7)];
                return angle;}) 
        .font("Impact")
        .fontSize(function(d) { return d.size; })
        .on("end", draw)
        .start();

        function draw(words) {
          d3.select("body").append("svg")
            .attr("width", 1400)
            .attr("height", 1000)
            .append("g")
            .attr("transform", "translate(700,500)")
            .selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", function(d) { return d.size + "px"; })
            .style("font-family", "Impact")
            .style("fill", function(d, i) { return fill(i); })
            .attr("text-anchor", "middle")
            .attr("transform", function(d) {
              return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
             })  
            .text(function(d) { return d.text; }); 
        }     

      return;
    }
  })
})
