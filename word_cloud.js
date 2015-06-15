var fill = d3.scale.category20();

// takes in a string of words delimited by commas, returns an array of objects
// of type {text: string, size: int}
function processData (x) {
    var words = x.split(',');
    var counts = {}

    for (var i = 0; i < words.length; i++) {
      var cur = words[i];
      counts[cur] = counts[cur] ? counts[cur] + 1 : 1;
    }

    var words_arr = [];
    var i = 0;
    for (var prop in counts) {
        words_arr[i] = {text: prop, size: counts[prop] * .02 };
        i = i + 1;
        // debugger;
    }
    // words_arr[0] = {text: "Yale", size: 100}
    
    words_arr.sort(function(a, b) {
      return b.size - a.size;
    });

    return words_arr.slice(0, 100);
}

$(document).ready(function() {
  $.ajax({
    type: "GET",
    url: "word_cloud.txt",
    dataType: "text",
    success: function(data) {
      // var klaus = [{text: "Klaus", size: 60}, {text: "Teuber", size: 70}];
      var counts = processData(data);//.substring(0, 10000000));

      d3.layout.cloud().size([300, 300])
        .words(counts) // [{text: "Sam", size: 60}, {text: "Peter", size: 70}])
        .padding(5)
        .rotate(function() { return ~~(Math.random() * 2) * 90; })
        .font("Impact")
        .fontSize(function(d) { return d.size; })
        .on("end", draw)
        .start();

        function draw(words) {
          d3.select("body").append("svg")
            .attr("width", 300)
            .attr("height", 300)
            .append("g")
            .attr("transform", "translate(150,150)")
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



