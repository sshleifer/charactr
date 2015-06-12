var fill = d3.scale.category20();

var getSize = function(d) {
  return {text: "HI", size: 60};
}

/* var words = read_file()
var counts = {}

for (var i = 0; i < words.length; i++) {
  var cur = arr[i];
  counts[cur] = counts[cur] ? counts[cur] + 1 : 1;
}

var words_arr = []
for (var i = 0; i < counts.length; i++) {
  words_arr[i] = {text: /* how to index/access object}
}
*/

/*
function readTextFile(file)
{
    var rawFile = new XMLHttpRequest();
    rawFile.open("GET", file, false);
    rawFile.onreadystatechange = function ()
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                var allText = rawFile.responseText;
                alert(allText);
            }
        }
    }
    rawFile.send(null);
}
*/

/*
var fso = new ActiveXObject("Scripting.FileSystemObject");
var txtFile = fso.OpenTextFile("C:\\myJS\\test.txt", 1, false, 0);
var fText = txtFile.Read(1000);
document.write(fText);
txtFile.Close();
fso = null;
*/

/*
readTextFile("word_cloud.txt");
*/

var selectedFile = $('word_cloud.txt').get(0, function() {alert('success');})
console.log(selectedFile);

console.log("hi");
/* console.log(allText); */

function processData (x) {
    return x;
}

function chart (x) {
    debugger
    console.log(x);
    return;
}

$(document).ready(function() {
  $.ajax({
    type: "GET",
    url: "word_cloud.txt",
    dataType: "text",
    success: function(data) {
      chart(processData(data));
      return;
    }
  })
})

d3.layout.cloud().size([300, 300])
  .words([{text: "Sam", size: 60}, {text: "Peter", size: 70}])
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
