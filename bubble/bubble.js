var data = {};

jQuery(document).ready(function($) {
    $.ajax({
        type: "GET",
        url: "bubble.txt",
        dataType: "json",
        success: function(json_data) {

            (function() {

                rec_obj = {}
                rec_obj["name"] = "friend"
                rec_obj["speeches"] = json_data.received
                sent_obj = {}
                sent_obj["name"] = "me"
                sent_obj["speeches"] = json_data.sent

                data.parties = [sent_obj, rec_obj].map(party);

            data.speakers = {
                "YOU": {name: "me", title: ""},
                "YASH WADHWA": {name: "Yash Wadhwa", title: "Candidate for Wisconsin State Assembly"}
            };

            var w_index = 0;
            var t_array = [];
            var temp_obj = {};

            for (; w_index < json_data.top_words.length; w_index++) {
                temp_obj = {};
                temp_obj["name"] = json_data.top_words[w_index].name;
                temp_obj["re"] = new RegExp(json_data.top_words[w_index].re, 'gi');
                temp_obj["x"] = json_data.top_words[w_index].x;
                temp_obj["y"] = json_data.top_words[w_index].y;
                t_array.push(temp_obj);
            }

            /*
            t_str = "\\b(haha)\\b";
            var regexp = new RegExp(t_str, 'gi');
            console.log(/\b(haha)\b/gi);
            console.log(regexp);
            */


            /*
            data.topics = [
            temp_obj,
            {name: "Yeah", re: /\b(yeah)\b/gi, x: 60, y: 110},
            {name: "Ya", re: /\b(ya)\b/gi, x: 60, y: 110},
            {name: "Workers", re: /\b(workers?)\b/gi, x: 179, y: 206}
            ].map(topic);
            */

            data.topics = t_array.map(topic)

            data.topic = function(name) {
                var t = topic({name: name, re: new RegExp("\\b(" + d3.requote(name) + ")\\b", "gi")}, data.topics.length);
                data.topics.push(t);
                return t;
            };

            function party(party) {
                party.speeches = party.speeches.map(speech);
                party.sections = sections(party.speeches);
                party.wordCount = d3.sum(party.sections, function(d) { return countWords(d.speech.text.substring(d.i, d.j)); });
                return party;
            }

            function speech(text, i) {
                return {text: text, id: i};
            }

            function sections(speeches) {
                var speakerRe = /(?:\n|^)([A-Z\.()\- ]+): /g,
                    sections = [];

                speeches.forEach(function(speech) {
                    var speakerName = "AUDIENCE",
                    match,
                    i = speakerRe.lastIndex = 0;
                while (match = speakerRe.exec(speech.text)) {
                    if (match.index > i) sections.push({speaker: speakerName, speech: speech, i: i, j: match.index});
                    speakerName = match[1];
                    i = speakerRe.lastIndex;
                }
                sections.push({speaker: speakerName, speech: speech, i: i, j: speech.text.length});
                });

                return sections.filter(function(d) { return !/^AUDIENCE\b/.test(d.speaker); });
            }

            function topic(topic, i) {
                topic.id = i;
                topic.count = 0;
                topic.cx = topic.x;
                topic.cy = topic.y;

                topic.parties = data.parties.map(function(party) {
                    var count = 0,
                    mentions = [];

                party.sections.forEach(function(section) {
                    var text = section.speech.text.substring(section.i, section.j), match;
                    topic.re.lastIndex = 0;
                    while (match = topic.re.exec(text)) {
                        ++count;
                        mentions.push({
                            topic: topic,
                            section: section,
                            i: section.i + match.index,
                            j: section.i + topic.re.lastIndex
                        });
                    }
                });

                topic.count += count = count / party.wordCount * 25e3;
                return {count: count, mentions: mentions};
                });

                return topic;
            }

            function countWords(text) {
                return text.split(/\s+/g)
                    .filter(function(d) { return d !== "â€”"; })
                    .length;
            }

            })();

            (function() {

                var width = 970,
                height = 640;

            var collisionPadding = 4,
                clipPadding = 4,
                minRadius = 16, // minimum collision radius
                maxRadius = 65, // also determines collision search radius
                maxMentions = 100, // don't show full transcripts
                activeTopic; // currently-displayed topic

            var formatShortCount = d3.format(",.0f"),
                formatLongCount = d3.format(".1f"),
                formatCount = function(d) { return (d < 10 ? formatLongCount : formatShortCount)(d); };

            var r = d3.scale.sqrt()
                .domain([0, d3.max(data.topics, function(d) { return d.count; })])
                .range([0, maxRadius]);

            var force = d3.layout.force()
                .charge(0)
                .size([width, height - 80])
                .on("tick", tick);

            var node = d3.select(".g-nodes").selectAll(".g-node"),
                label = d3.select(".g-labels").selectAll(".g-label"),
                arrow = d3.select(".g-nodes").selectAll(".g-note-arrow");

            d3.select(".g-nodes").append("rect")
                .attr("class", "g-overlay")
                .attr("width", width)
                .attr("height", height)
                .on("click", clear);

            d3.select(window)
                .on("hashchange", hashchange);

            d3.select("#g-form")
                .on("submit", submit);

            updateTopics(data.topics);
            hashchange();

            // Update the known topics.
            function updateTopics(topics) {
                topics.forEach(function(d) {
                    d.r = r(d.count);
                    d.cr = Math.max(minRadius, d.r);
                    d.k = fraction(d.parties[0].count, d.parties[1].count);
                    if (isNaN(d.k)) d.k = .5;
                    if (isNaN(d.x)) d.x = (1 - d.k) * width + Math.random();
                    d.bias = .5 - Math.max(.1, Math.min(.9, d.k));
                });
                force.nodes(data.topics = topics).start();
                updateNodes();
                updateLabels();
                updateArrows();
                tick({alpha: 0}); // synchronous update
            }

            // Update the displayed nodes.
            function updateNodes() {
                node = node.data(data.topics, function(d) { return d.name; });

                node.exit().remove();

                var nodeEnter = node.enter().append("a")
                    .attr("class", "g-node")
                    .attr("xlink:href", function(d) { return "#" + encodeURIComponent(d.name); })
                    .call(force.drag)
                    .call(linkTopic);

                var democratEnter = nodeEnter.append("g")
                    .attr("class", "g-democrat");

                democratEnter.append("clipPath")
                    .attr("id", function(d) { return "g-clip-democrat-" + d.id; })
                    .append("rect");

                democratEnter.append("circle");

                var republicanEnter = nodeEnter.append("g")
                    .attr("class", "g-republican");

                republicanEnter.append("clipPath")
                    .attr("id", function(d) { return "g-clip-republican-" + d.id; })
                    .append("rect");

                republicanEnter.append("circle");

                nodeEnter.append("line")
                    .attr("class", "g-split");

                node.selectAll("rect")
                    .attr("y", function(d) { return -d.r - clipPadding; })
                    .attr("height", function(d) { return 2 * d.r + 2 * clipPadding; });

                node.select(".g-democrat rect")
                    .style("display", function(d) { return d.k > 0 ? null : "none" })
                    .attr("x", function(d) { return -d.r - clipPadding; })
                    .attr("width", function(d) { return 2 * d.r * d.k + clipPadding; });

                node.select(".g-republican rect")
                    .style("display", function(d) { return d.k < 1 ? null : "none" })
                    .attr("x", function(d) { return -d.r + 2 * d.r * d.k; })
                    .attr("width", function(d) { return 2 * d.r; });

                node.select(".g-democrat circle")
                    .attr("clip-path", function(d) { return d.k < 1 ? "url(#g-clip-democrat-" + d.id + ")" : null; });

                node.select(".g-republican circle")
                    .attr("clip-path", function(d) { return d.k > 0 ? "url(#g-clip-republican-" + d.id + ")" : null; });

                node.select(".g-split")
                    .attr("x1", function(d) { return -d.r + 2 * d.r * d.k; })
                    .attr("y1", function(d) { return -Math.sqrt(d.r * d.r - Math.pow(-d.r + 2 * d.r * d.k, 2)); })
                    .attr("x2", function(d) { return -d.r + 2 * d.r * d.k; })
                    .attr("y2", function(d) { return Math.sqrt(d.r * d.r - Math.pow(-d.r + 2 * d.r * d.k, 2)); });

                node.selectAll("circle")
                    .attr("r", function(d) { return r(d.count); });
            }

            // Update the displayed node labels.
            function updateLabels() {
                label = label.data(data.topics, function(d) { return d.name; });

                label.exit().remove();

                var labelEnter = label.enter().append("a")
                    .attr("class", "g-label")
                    .attr("href", function(d) { return "#" + encodeURIComponent(d.name); })
                    .call(force.drag)
                    .call(linkTopic);

                labelEnter.append("div")
                    .attr("class", "g-name")
                    .text(function(d) { return d.name; });

                labelEnter.append("div")
                    .attr("class", "g-value");

                label
                    .style("font-size", function(d) { return Math.max(8, d.r / 2) + "px"; })
                    .style("width", function(d) { return d.r * 2.5 + "px"; });

                // Create a temporary span to compute the true text width.
                label.append("span")
                    .text(function(d) { return d.name; })
                    .each(function(d) { d.dx = Math.max(d.r * 2.5, this.getBoundingClientRect().width); })
                    .remove();

                label
                    .style("width", function(d) { return d.dx + "px"; })
                    .select(".g-value")
                    .text(function(d) { return formatShortCount(d.parties[0].count) + " - " + formatShortCount(d.parties[1].count); });

                // Compute the height of labels when wrapped.
                label.each(function(d) { d.dy = this.getBoundingClientRect().height; });
            }

            // Update the active topic.
            function updateActiveTopic(topic) {
                d3.selectAll(".g-head").attr("class", topic ? "g-head g-has-topic" : "g-head g-hasnt-topic");
                if (activeTopic = topic) {
                    node.classed("g-selected", function(d) { return d === topic; });
                    updateMentions(findMentions(topic));
                    d3.selectAll(".g-head a").text(topic.name);
                    d3.select(".g-democrat .g-head span.g-count").text(formatCount(topic.parties[0].count));
                    d3.select(".g-republican .g-head span.g-count").text(formatCount(topic.parties[1].count));
                } else {
                    node.classed("g-selected", false);
                    updateMentions(sampleMentions());
                    d3.selectAll(".g-head a").text("various topics");
                    d3.selectAll(".g-head span.g-count").text("some number of");
                }
            }

            // Update displayed excerpts.
            function updateMentions(mentions) {
                var column = d3.selectAll(".g-mentions")
                    .data(mentions);

                column.select(".g-truncated")
                    .style("display", function(d) { return d.truncated ? "block" : null; });

                var mention = column.selectAll(".g-mention")
                    .data(groupMentionsBySpeaker, function(d) { return d.key; });

                mention.exit().remove();

                mention.selectAll("p")
                    .remove();

                var mentionEnter = mention.enter().insert("div", ".g-truncated")
                    .attr("class", "g-mention");

                mentionEnter.append("div")
                    .attr("class", "g-speaker")
                    .text(function(d) { var s = data.speakers[d.key]; return s ? s.name : d.key; });

                mentionEnter.append("div")
                    .attr("class", "g-speaker-title")
                    .text(function(d) { var s = data.speakers[d.key]; return s && s.title; });

                mention
                    .sort(function(a, b) { return b.values.length - a.values.length; });

                var p = mention.selectAll("p")
                    .data(function(d) { return d.values; })
                    .enter().append("p")
                    .html(function(d) { return d.section.speech.text.substring(d.start, d.end).replace(d.topic.re, "<a>$1</a>"); });

                if (activeTopic) {
                    p.attr("class", "g-hover");
                } else {
                    p.each(function(d) {
                        d3.select(this).selectAll("a")
                        .datum(d.topic)
                        .attr("href", "#" + encodeURIComponent(d.topic.name))
                        .call(linkTopic);
                    });
                }
            }

            // Bind the arrow path elements with their associated topic.
            function updateArrows() {
                arrow = arrow.data(
                        data.topics.filter(function(d) { return d.arrow; }),
                        function(d) { return this.id ? this.id.substring(8) : d.arrow; });
            }

            // Return a random sample of mentions per party, one per topic.
            // Mentions are returned in chronological order.
            function sampleMentions() {
                return data.parties.map(function(party, i) {
                    return data.topics
                    .map(function(d) { return d.parties[i].mentions; })
                    .filter(function(d) { return d.length; })
                    .map(function(d) { return d[Math.floor(Math.random() * d.length)]; })
                    .sort(orderMentions);
                });
            }

            // Return displayable mentions per party for the specified topic.
            // If too many, a random sample of matching mentions is returned.
            // Mentions are returned in chronological order.
            function findMentions(topic) {
                return data.parties.map(function(party, i) {
                    var mentions = topic.parties[i].mentions;
                    if (mentions.length > maxMentions) {
                        shuffle(mentions).length = maxMentions;
                        mentions.sort(orderMentions);
                        mentions.truncated = true;
                    }
                    return mentions;
                });
            }

            // Group mentions by speaker, collapse overlapping excerpts.
            function groupMentionsBySpeaker(mentions) {
                return d3.nest()
                    .key(function(d) { return d.section.speaker; })
                    .rollup(collapseMentions)
                    .entries(mentions);
            }

            // Given an array of mentions, computes the start and end point of the context
            // excerpt, and then collapses any overlapping excerpts.
            function collapseMentions(mentions) {
                var sentenceRe = /([!?.)]+)\s+/g, // sentence splitting requires NLP
                    i,
                    n = mentions.length,
                    d0,
                    d1;

                // First compute the excerpt contexts.
                for (i = 0; i < n; ++i) {
                    d0 = mentions[i];
                    d0.start = excerptStart(d0);
                    d0.end = excerptEnd(d0);
                }

                // Then collapse any overlapping excerpts (from the same speech).
                for (i = 1, d1 = mentions[0]; i < n; ++i) {
                    d0 = d1;
                    d1 = mentions[i];
                    if (d1.section.speech.id === d0.section.speech.id
                            && d1.start >= d0.start
                            && d1.start < d0.end) {
                        d1.start = -1;
                        d0.end = d1.end;
                        d1 = d0;
                    }
                }

                // Returns the start index of the excerpt for the specified mention.
                function excerptStart(mention) {
                    var i = sentenceRe.lastIndex = Math.max(mention.section.i, mention.i - 80), match;
                    while (match = sentenceRe.exec(mention.section.speech.text)) {
                        if (match.index < mention.i - 20) return match.index + match[0].length;
                        if (i <= mention.section.i) break;
                        sentenceRe.lastIndex = i = Math.max(mention.section.i, i - 20);
                    }
                    return mention.section.i;
                }

                // Returns the end index of the excerpt for the specified mention.
                function excerptEnd(mention) {
                    var i = mention.section.j, match;
                    sentenceRe.lastIndex = mention.j + 40;
                    match = sentenceRe.exec(mention.section.speech.text);
                    return match ? Math.min(match.index + match[1].length, i) : i;
                }

                return mentions.filter(function(d) { return d.start >= 0; });
            }

            // Orders mentions chronologically: by speech and position within speech.
            function orderMentions(a, b) {
                return a.section.speech.id - b.section.speech.id || a.i - b.i;
            }

            // Assign event handlers to topic links.
            function linkTopic(a) {
                a   .on("click", click)
                    .on("mouseover", mouseover)
                    .on("mouseout", mouseout);
            }

            // Returns the topic matching the specified name, approximately.
            // If no matching topic is found, returns undefined.
            function findTopic(name) {
                for (var i = 0, n = data.topics.length, t; i < n; ++i) {
                    if ((t = data.topics[i]).name === name || new RegExp("^" + (t = data.topics[i]).re.source + "$", "i").test(name)) {
                        return t;
                    }
                }
            }

            // Returns the topic matching the specified name, approximately.
            // If no matching topic is found, a new one is created.
            function findOrAddTopic(name) {
                var topic = findTopic(name);
                if (!topic) {
                    topic = data.topic(name.substring(0, 1).toUpperCase() + name.substring(1));
                    topic.y = 0;
                    updateTopics(data.topics);
                }
                return topic;
            }

            // Simulate forces and update node and label positions on tick.
            function tick(e) {
                node
                    .each(bias(e.alpha * 105))
                    .each(collide(.5))
                    .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

                label
                    .style("left", function(d) { return (d.x - d.dx / 2) + "px"; })
                    .style("top", function(d) { return (d.y - d.dy / 2) + "px"; });

                arrow.style("stroke-opacity", function(d) {
                    var dx = d.x - d.cx, dy = d.y - d.cy;
                    return dx * dx + dy * dy < d.r * d.r ? 1: 0;
                });
            }

            // A left-right bias causing topics to orient by party preference.
            function bias(alpha) {
                return function(d) {
                    d.x += d.bias * alpha;
                };
            }

            // Resolve collisions between nodes.
            function collide(alpha) {
                var q = d3.geom.quadtree(data.topics);
                return function(d) {
                    var r = d.cr + maxRadius + collisionPadding,
                        nx1 = d.x - r,
                        nx2 = d.x + r,
                        ny1 = d.y - r,
                        ny2 = d.y + r;
                    q.visit(function(quad, x1, y1, x2, y2) {
                        if (quad.point && (quad.point !== d) && d.other !== quad.point && d !== quad.point.other) {
                            var x = d.x - quad.point.x,
                        y = d.y - quad.point.y,
                        l = Math.sqrt(x * x + y * y),
                        r = d.cr + quad.point.r + collisionPadding;
                    if (l < r) {
                        l = (l - r) / l * alpha;
                        d.x -= x *= l;
                        d.y -= y *= l;
                        quad.point.x += x;
                        quad.point.y += y;
                    }
                        }
                        return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
                    });
                };
            }

            // Fisherâ€“Yates shuffle.
            function shuffle(array) {
                var m = array.length, t, i;
                while (m) {
                    i = Math.floor(Math.random() * m--);
                    t = array[m];
                    array[m] = array[i];
                    array[i] = t;
                }
                return array;
            }

            // Given two quantities a and b, returns the fraction to split the circle a + b.
            function fraction(a, b) {
                var k = a / (a + b);
                if (k > 0 && k < 1) {
                    var t0, t1 = Math.pow(12 * k * Math.PI, 1 / 3);
                    for (var i = 0; i < 10; ++i) { // Solve for theta numerically.
                        t0 = t1;
                        t1 = (Math.sin(t0) - t0 * Math.cos(t0) + 2 * k * Math.PI) / (1 - Math.cos(t0));
                    }
                    k = (1 - Math.cos(t1 / 2)) / 2;
                }
                return k;
            }

            // Update the active topic on hashchange, perhaps creating a new topic.
            function hashchange() {
                var name = decodeURIComponent(location.hash.substring(1)).trim();
                updateActiveTopic(name && name != "!" ? findOrAddTopic(name) : null);
            }

            // Trigger a hashchange on submit.
            function submit() {
                var name = this.search.value.trim();
                location.hash = name ? encodeURIComponent(name) : "!";
                this.search.value = "";
                d3.event.preventDefault();
            }

            // Clear the active topic when clicking on the chart background.
            function clear() {
                location.replace("#!");
            }

            // Rather than flood the browser history, use location.replace.
            function click(d) {
                location.replace("#" + encodeURIComponent(d === activeTopic ? "!" : d.name));
                d3.event.preventDefault();
            }

            // When hovering the label, highlight the associated node and vice versa.
            // When no topic is active, also cross-highlight with any mentions in excerpts.
            function mouseover(d) {
                node.classed("g-hover", function(p) { return p === d; });
                if (!activeTopic) d3.selectAll(".g-mention p").classed("g-hover", function(p) { return p.topic === d; });
            }

            // When hovering the label, highlight the associated node and vice versa.
            // When no topic is active, also cross-highlight with any mentions in excerpts.
            function mouseout(d) {
                node.classed("g-hover", false);
                if (!activeTopic) d3.selectAll(".g-mention p").classed("g-hover", false);
            }

            })();

        }
    });
});
