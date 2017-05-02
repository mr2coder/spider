$(document).ready(function() {

    //chart initial
    myChart = echarts.init(document.getElementById('body-graph'));

    function refrsh_tables(data) {
        //get table data from mongo
        var data = data;
        for (var i = 0; i < data.length; i++) {
            /*
            maybe use this later...
            -----------------------
            if (data[i]['status'] == 0) {
                data[i]['del'] = "已完成"
            } else {
                data[i]['del'] = '<button type="button" style="float: left;" name="close" class="close" data-dismiss="alert">' + '<span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>';

            }
            */
            data[i]['content'] = data[i]['qwords'] + data[i]['title'] + data[i]['author'] + data[i]['insititution'];
            data[i]['more'] = '<button type="button" style="float: left;" name="more" class="more" data-dismiss="alert" >' + '<span class="glyphicon glyphicon-stats"  aria-hidden="true"></span></button>';
            data[i]['update'] = '<button type="button" style="float: left;" id="download" name="download" class="more" data-toggle="modal" data-target="#paperModal"><span class="glyphicon glyphicon-refresh" aria-hidden="true"></span></button>';
            data[i]['del'] = '<button type="button" style="float: left;" name="close" class="close" data-dismiss="alert">' + '<span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>';
        }
        $('#already_exist').DataTable({
            responsive: true,
            "bDestroy": true,
            data: data,
            scrollY: 500,
            "bDeferRender": true,
            columns: [
                { data: 'content' },
                { data: 'time' },
                { data: 'feq' },
                { data: 'count' },
                { data: 'del' },
                { data: 'more' },
                { data: 'update' }
            ]
        });
    }

    //initial already_exist table
    $.getJSON('/api_patent_already_exist_data', {
        a: 1
    }, function(data) {
        refrsh_tables(data)
    });

    $('#add').bind('click', function() {
        title = $('input[name="name"]').val();
        qwords = $('input[name="qwords"]').val();
        author = $('input[name="author"]').val();
        insititution = $('input[name="insititution"]').val();
        begin = $('input[name="begin"]').val();
        end = $('input[name="end"]').val();
        time = $('select[name="times"]').val();
        if (title == '' && qwords == '' && insititution == '' && author == '') {
            alert('内容作者不能同时为空！');
            return false
        }
        if (begin > end) {
            alert('起始年不能大于结束年！');
            return false
        }
        $.post('/patent_add_item', {
            title: title,
            qwords: qwords,
            author: author,
            insititution: insititution,
            begin: begin,
            end: end,
            time: time
        }, function(data) {
            if (data == null) {
                alert("任务已存在，添加失败！");
                return false;
            }
            var date = new Date()
            var time = date.getFullYear() + "/" + date.getMonth() + "/" + date.getDate();
            refrsh_tables(data)
        });
        return false;
    });

    $('#begin').blur(function() {
        var date = new Date()
        var value = this.value
        if (!(value > 1900 && value < date.getFullYear() + 1) && value != '') {
            alert('起始年格式有误！')
        }
    });

    $('#end').blur(function() {
        var date = new Date()
        var value = this.value
        if (!(value > 1900 && value < date.getFullYear() + 1) && value != '') {
            alert('结束年格式有误！')
        }
    });


    $('#already_exist').on('click', 'button.close', function() {
        if (confirm('确认要删除么？')) {
            var button = this
            var table = $('#already_exist').DataTable();
            var data = table.row($(this).parents('tr')).data();
            $.post('/api_patent_delete_task', {
                spider_id: data['_id']
            }, function(data) {
                if (data == 0) {
                    $('#already_exist').DataTable()
                        .row($(button).parents('tr'))
                        .remove()
                        .draw();
                    set_detail('head-detail', [])
                } else {
                    alert('删除失败');
                }

            });
        }
    });


    //more button
    $('#already_exist').on('click', 'tr', function() {
        var table = $('#already_exist').DataTable();
        var data = table.row(this).data()
        if (data != null) {
            $.post('/api_patent_task_tr_click', {
                _id: data['_id']
            }, function(data) {
                set_gragh('head-graph', data['xy_value'])
                set_detail('head-detail', data['content'])
            });
        }
    });

    //dynamic setting graph size:<length>,<wight>
    $(window).resize(function() {
        myChart.resize();
    });


    //
    function set_detail(head_id, content) {
        $('#patent_list').DataTable({
            "bDestroy": true,
            data: content,
            scrollY: 500,
            "bDeferRender": true,
            columns: [
                { data: "title" },
                { data: "t_id" },
                { data: "r_date" },
                { data: "o_id" },
                { data: "o_date" },
                { data: "icp_id" },
                { data: "institution" },
                { data: "author" },
                { data: "proxie" },
                { data: "proxy_insititution" },
                { data: "spidertime" }

            ]
        });

    }

    function set_gragh(head_id, xy_value) {
        //初始化图表
        // 基于准备好的dom，初始化echarts图表
        // var myChart = echarts.init(document.getElementById('body-detail'));
        var option = {
            title: {
                text: '最近爬虫数量变化',
                subtext: ''
            },
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                data: ['万方']
            },
            toolbox: {
                show: true,
                feature: {
                    mark: {
                        show: true
                    },
                    dataView: {
                        show: true,
                        readOnly: false
                    },
                    magicType: {
                        show: true,
                        type: ['line', 'bar']
                    },
                    restore: {
                        show: true
                    },
                    saveAsImage: {
                        show: true
                    }
                }
            },
            calculable: true,
            xAxis: [{
                type: 'category',
                boundaryGap: false,
                data: xy_value['x_value']
            }],
            yAxis: [{
                type: 'value',
                min: 0,
                max: 1000,
                axisLabel: {
                    formatter: '{value} 条'
                }
            }],
            series: [{
                name: '条数',
                type: 'line',
                data: xy_value['y_value'],
                markPoint: {
                    data: [{
                        type: 'max',
                        name: '最大值'
                    }, {
                        type: 'min',
                        name: '最小值'
                    }]
                },
                markLine: {
                    data: [{
                        type: 'average',
                        name: '平均值'
                    }]
                }
            }]
        };

        // 为echarts对象加载数据 
        myChart.setOption(option);
    }

    var refresh_task = null;
    $('#already_exist').on('click', '#download', function() {
        var table = $('#already_exist').DataTable();
        var data = table.row($(this).parents('tr')).data()
            //download button action
        console.log(data)
        $.post('/api_patent_download_begin', {
            _id: data['_id'],
        }, function(data) {});
        if (refresh_task == null) {
            $('#log').html("");
            $('#log').append('<p>' + $('<div/>').text('任务开始：').html());
            refresh_task = setInterval(refresh_log, 1000); //
        }

    });

    function refresh_log(_id) {
        // body...
        $.post('/api_patent_refresh_log', {
            _id: _id
        }, function(data) {
            $('#log').append('<p>' + $('<div/>').text(data['line']).html());
            $('#log').scrollTop($('#log')[0].scrollHeight); //Keep the bottom alignment
            if (data['line'].slice(0, 7) == 'Success') {
                window.clearInterval(refresh_task);
                refresh_task = null;
            }
        });
    }


    $('#disconnect').on('click', function() {
        stop_refresh_log()
        return false;

    });

    function stop_refresh_log() {
        // body...
        $.post('/api_patent_download_end', {}, function(data) {
            if (data == 0) {
                window.clearInterval(refresh_task);
                refresh_task = null;
                $('#log').append('<p>' + $('<div/>').text('task should be shutdown...').html());
                $('#log').scrollTop($('#log')[0].scrollHeight); //Keep the bottom alignment
            }
        });

    }

});
