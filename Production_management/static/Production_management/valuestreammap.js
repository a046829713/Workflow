var leadtimedata = []


function drawchart(motherpd, qty_num, LeadTime) {
    let currentMotherpd = "";
    let currentqty_num = "";
    let currentLeadTime = "";
    let maxnum = 1
    let enough = []
    let enough_parent = []

    function parser_length(nodes) {
        // 當有子類物件時進行 沒有則不做任何動作
        if ('children' in nodes) {
            if (nodes.children.length >= 1) {
                for (let i = 0; i < nodes.children.length; i++) {
                    maxnum = Math.max(maxnum, nodes.children.length)
                    parser_length(nodes.children[i])
                }
            }
        }
        return maxnum
    }

    function parser_checkenough(nodes, qty_num) {
        if ('data' in nodes) {
            // 當我是false 的時候繼續往下走
            let usefull_qty = isNaN(parseInt(nodes.data.usefull_qty)) ? 0 : parseInt(nodes.data.usefull_qty);
            let consume = isNaN(parseInt(nodes.data.consume)) ? 1 : parseFloat(nodes.data.consume);
            
            let int_qty_num = parseInt(qty_num)

            if (usefull_qty < consume * int_qty_num) {
                // 當有子類物件時進行
                if ('children' in nodes) {
                    if (nodes.children.length >= 1) {
                        for (let i = 0; i < nodes.children.length; i++) {
                            parser_checkenough(nodes.children[i], int_qty_num)

                        }
                    }
                }
            }

            enough.push([nodes.data.name, usefull_qty >= consume * int_qty_num])
            enough_parent.push(nodes.data.name)
        }
    }

    function checkparentenout(d) {
        // 在繪圖的時候要檢查每一個母階有沒有在enough裡面,只要有一個母階不再裡面,代表那整條線都不需要繪製出來
        for (let x = 0; x < enough.length; x++) {
            checktodraw = true;
            if (d.data.name === enough[x][0] && enough[x][1] === false) {
                // 進一步確認所有母階
                function _checkparentenout(node) {
                    // 確認所有母階是否存在於enough
                    if (node.parent) {
                        if (!enough_parent.includes(node.parent.data.name)) {

                            checktodraw = false;


                        }
                        if (node.parent.parent) {

                            _checkparentenout(node.parent.parent)
                        }
                    }
                }
                _checkparentenout(d)

                if (checktodraw) {
                    return "#BD2A2E"
                } else {
                    return "#CACACA"
                }

            }
        }

    }


    function getparentlink(nodes) {
        let parentid = [];

        function _getparentlink(node) {
            if (node.parent) {
                if (node.parent.data.name) {
                    parentid.push([node.parent.data.name, node.data.name]);
                }
                _getparentlink(node.parent);
            }
        }

        _getparentlink(nodes);

        return parentid;
    }

    function gettextdata(object, traget_str) {
        let out_str = ''

        if (traget_str === 'order_out_price') {
            if (d3.select(object.parentNode)._groups[0][0].__data__.data.order_out_price) {
                out_str = `委外價格:${d3.select(object.parentNode)._groups[0][0].__data__.data.order_out_price}`
            }

        } else if (traget_str === 'Make_CN_name') {
            if (d3.select(object.parentNode)._groups[0][0].__data__.data.Make_CN_name) {
                out_str = `製令名稱:${d3.select(object.parentNode)._groups[0][0].__data__.data.Make_CN_name}`
            }

        } else if (traget_str === 'prod_name') {
            if (d3.select(object.parentNode)._groups[0][0].__data__.data.prod_name) {
                out_str = `品名規格:${d3.select(object.parentNode)._groups[0][0].__data__.data.prod_name}`
            }

        } else if (traget_str === 'safe_qty') {
            if (d3.select(object.parentNode)._groups[0][0].__data__.data.safe_qty) {
                out_str = `安庫:${d3.select(object.parentNode)._groups[0][0].__data__.data.safe_qty}`
            }
        } else if (traget_str === 'fact_na') {
            if (d3.select(object.parentNode)._groups[0][0].__data__.data.fact_na) {
                out_str = `廠商名稱:${d3.select(object.parentNode)._groups[0][0].__data__.data.fact_na}`
            }
        } else if (traget_str === 'usefull_qty') {
            if (d3.select(object.parentNode)._groups[0][0].__data__.data.usefull_qty) {
                out_str = `現有庫存可用量:${d3.select(object.parentNode)._groups[0][0].__data__.data.usefull_qty}`
            }
        }
        else if (traget_str === 'leadtime') {
            if (d3.select(object.parentNode)._groups[0][0].__data__.data.Time.length > 1) {
                out_str = `LeadTime:${d3.select(object.parentNode)._groups[0][0].__data__.data.Time.replace('.0', '')}`
            }
        }
        else if (traget_str === 'Name') {
            if (d3.select(object.parentNode)._groups[0][0].__data__.data.name) {
                out_str = `料號名稱:${d3.select(object.parentNode)._groups[0][0].__data__.data.name}`
            }

        }
        else if (traget_str === 'MKtime') {
            if (d3.select(object.parentNode)._groups[0][0].__data__.data.MKtime) {
                out_str = `製程天數:${d3.select(object.parentNode)._groups[0][0].__data__.data.MKtime}`
            }
        }
        else if (traget_str === 'consume') {
            if (d3.select(object.parentNode)._groups[0][0].__data__.data.consume) {
                out_str = `單位用量:${d3.select(object.parentNode)._groups[0][0].__data__.data.consume}`
            }
        }


        return out_str;
    }

    function maxStringLength(data) {
        let max_len = 0
        for (let x = 0; x < data.length; x++) {
            if (max_len < data[x].getComputedTextLength()) {
                max_len = data[x].getComputedTextLength()
            }
        }


        return max_len
    }
    async function draw(motherpd, qty_num, LeadTime) {
        if (motherpd !== currentMotherpd || qty_num !== currentqty_num || LeadTime !== currentLeadTime) { // 判斷傳入的 motherpd 是否與當前的不同
            leadtimedata = [] // 重製資料

            currentMotherpd = motherpd; // 更新當前的 motherpd
            currentqty_num = qty_num;
            currentLeadTime = LeadTime;
            // 清空 SVG
            d3.select("svg").remove();

            // Data
            // const treeData = await d3.json('tree.json')

            const treeData = await d3.json($("#treeApi").text() + `?motherpd=${motherpd}`)

            if (LeadTime) {
                leadtimedata = await d3.json($("#treeApiCheckTime").text() + `?motherpd=${motherpd}&useleadtime=${LeadTime}`)
            }

            // 選擇畫面的原素，並關閉
            $("#maskArea").css("width", "0%");

            //  assigns the data to a hierarchy using parent-child relationships
            let nodes = d3.hierarchy(treeData, d => d.children);

            // 取得那些母階要畫成紅色
            parser_checkenough(nodes, qty_num)
            const node_width = parser_length(nodes)


            // set the dimensions and margins of the diagram
            const margin = { top: 15, right: 20, bottom: 30, left: 20 };
            const width = nodes.height * 250;
            const height = node_width * 115;


            // declares a tree layout and assigns the size
            const treemap = d3.tree().size([height * 0.92, width * 0.8]);


            // maps the node data to the tree layout
            nodes = treemap(nodes);

            // append the svg object to the body of the page
            // appends a 'group' element to 'svg'
            // moves the 'group' element to the top left margin
            const svg = d3.select("body").append("svg")
                .attr("width", width + margin.left + margin.right + 600)
                .attr("height", height + margin.top + margin.bottom + 600)

            const g = svg.append("g")
                .attr("transform",
                    "translate(" + margin.left + "," + margin.top + ")");



            // adds the links between the nodes
            const link = g.selectAll(".link")
                .data(nodes.descendants().slice(1))
                .enter().append("path")
                .attr("class", "link")
                .attr('data-parent-id', d => d.parent.data.name)
                .attr('data-id', d => d.data.name)
                .attr("d", d => {
                    return "M" + d.y + "," + d.x
                        + "C" + (d.y + d.parent.y) / 2 + "," + d.x
                        + " " + (d.y + d.parent.y) / 2 + "," + d.parent.x
                        + " " + d.parent.y + "," + d.parent.x;
                })
                .style("stroke", "#CACACA")
                .style("stroke-width", "3px")
                .on("mouseover", function (event, d) {
                    // Change the stroke of the link
                    d3.select(this)
                        .style("stroke", "#878787")
                        .style("stroke-width", "4px");
                    let targets = getparentlink(d);

                    // Select links with the same parent ID and change their stroke color
                    for (i = 0; i < targets.length; i++) {
                        d3.select('path[data-parent-id="' + targets[i][0] + '"][data-id="' + targets[i][1] + '"]')
                            .style("stroke", "#878787")
                            .style("stroke-width", "4px");
                    }

                }).on("mouseout", function (event, d) {
                    // Change the stroke color back to the original green
                    d3.select(this)
                        .style("stroke", function (d) {
                            return checkparentenout(d)
                        })
                        .style("stroke-width", "3px");

                    // Select links with the same parent ID and change their stroke color back to the original green
                    let targets = getparentlink(d);
                    for (i = 0; i < targets.length; i++) {
                        d3.select('path[data-parent-id="' + targets[i][0] + '"][data-id="' + targets[i][1] + '"]')
                            .style("stroke", function (d) {
                                return checkparentenout(d)
                            })
                            .style("stroke-width", "3px");
                    }
                })
                ;


            d3.selectAll(".link")
                .style("stroke", function (d) {
                    return checkparentenout(d)
                })

            // adds each node as a group
            const node = g.selectAll(".node")
                .data(nodes.descendants())
                .enter().append("g")
                .classed("node", true)
                .attr("transform", d => "translate(" + d.y + "," + d.x + ")");


            // adds the circle to the node
            node.append("circle")
                .attr("r", d => 3);


            node.selectAll("circle")
                .style("stroke", (d) => {
                    if (d.data.safe_qty > 0) {
                        return "#F28705"
                    } else {
                        return "#72A404"
                    }

                })
                ;

            node.selectAll("circle")
                .on("mouseover", function (event, d) {
                    // 创建 tooltip
                    d3.select(this.parentNode.parentNode)
                        .append("rect")
                        .attr("class", "tooltip-bg")
                        .attr("x", "0")
                        .attr("y", "0")
                        .style("fill", "#D9D0C5");


                    d3.select(this.parentNode.parentNode)
                        .append("text")
                        // .data()
                        .attr("class", "tooltip-text")
                        .attr("x", 5)
                        .attr("y", 25)

                        ;

                    var match = d3.select(this.parentNode).attr("transform").match(/translate\((\d+),([\d\.]+)\)/);
                    var trans_x = (parseFloat(match[1]) + 5).toFixed(5);;
                    var trans_y = match[2];
                    d3.selectAll("rect")
                        .attr("transform", d => "translate(" + trans_x + "," + trans_y + ")")
                    d3.selectAll(".tooltip-text")
                        .attr("transform", d => "translate(" + trans_x + "," + trans_y + ")")

                    // 選擇文本框並插入兩個 tspan 元素
                    d3.select(".tooltip-text")
                        .selectAll("tspan")
                        .data([
                            { text: gettextdata(this, "Name") },
                            { text: gettextdata(this, "Make_CN_name") },
                            { text: gettextdata(this, "order_out_price") },
                            { text: gettextdata(this, "prod_name") },
                            { text: gettextdata(this, "safe_qty") },
                            { text: gettextdata(this, "fact_na") },
                            { text: gettextdata(this, "usefull_qty") },
                            { text: gettextdata(this, "leadtime") },
                            { text: gettextdata(this, "MKtime") },
                            { text: gettextdata(this, "consume") },

                        ].filter(d => d.text !== ''))
                        .enter()
                        .append("tspan")
                        .attr("class", "tspan-text")
                        .text(d => d.text)
                        .attr("fill", "#8C6F6C")
                        .attr("font-size", "24px")
                        .attr("font-weight", "bold")
                        .attr("x", 0)
                        .attr("y", (d, i) => i === 0 ? 20 : 20 + i * 25);
                    ;

                    // 根據文本長度更改顯示長度
                    d3.select('rect')
                        .attr('width', `${maxStringLength(d3.selectAll(".tspan-text")._groups[0]) + 10}px`)
                        .attr('height', '250px')
                        .attr("rx", 10)
                        .attr("ry", 10)
                        .attr("stroke-width", 2)
                        .attr("stroke", "#BF6415")
                        ;



                }).on("mouseout", function (event, d) {
                    // 删除 tooltip
                    d3.select(this.parentNode.parentNode).selectAll(".tooltip-bg, .tooltip-text, .tspan-text").remove();
                });



            // adds the text to the node
            node.append("text")
            node.selectAll("text")
                .append('tspan')
                .text(d => {
                    return d.data.name
                })
                .attr("dy", "1em")
                .attr("dx", "-1em")
                .attr("fill", (d) => {
                    if (d.data.name.indexOf('[') !== -1) {
                        return "#04BF8A"

                    } else {
                        if (leadtimedata.includes(d.data.name)) {

                            return "#F28705"
                        }
                    }
                }
                );

        }
    }
    draw(motherpd, qty_num, LeadTime)
}




async function generateopenmaterialsExcel() {
    if (document.querySelector('svg')) {    // 創建Excel數據數組
        let PROD_NO = $("#motherpd").val()
        let qty_num = $("#QTY").val()


        $("#maskArea").css("width", "100%");
        const openmaterials_not_enough_data = await d3.json($("#getopenmaterials").text() + `?PROD_NO=${PROD_NO}&qty_num=${qty_num}`)
        $("#maskArea").css("width", "0%");
        var data = [
            ['母階料號', '料號', '詢單數量'],

        ];
        for (var i = 0; i < openmaterials_not_enough_data.length; i++) {
            data.push([PROD_NO, openmaterials_not_enough_data[i], qty_num]);
        }

        // 創建工作簿對象
        var workbook = XLSX.utils.book_new();

        // 將數據添加到工作表中
        var worksheet = XLSX.utils.aoa_to_sheet(data);
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');

        // 將Excel文件下載到本地
        XLSX.writeFile(workbook, `${PROD_NO}.xlsx`);
    }else{
        alert("請先進行查詢，才可以匯出");
    }
}