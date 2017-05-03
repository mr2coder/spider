$(document).ready(function() {
    var socket = null;
    var connect_tag = false;

    //chart initial
    myChart = echarts.init(document.getElementById('body-graph'));

    function refrsh_tables(data) {
        //get table data from mongo
        var data = data;
        for (var i = 0; i < data.length; i++) {

            data[i]['del'] = '<button type="button" style="float: left;" name="close" class="close" data-dismiss="alert">' + '<span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>';
            data[i]['more'] = '<button type="button" style="float: left;" id="more" name="more" class="more" data-dismiss="alert" >' + '<span class="glyphicon glyphicon-stats"  aria-hidden="true"></span></button>';
            data[i]['update'] = '<button type="button" style="float: left;" id="download" name="download" class="more" data-toggle="modal" data-target="#paperModal"><span class="glyphicon glyphicon-refresh" aria-hidden="true"></span></button>';
        }
        $('#already_exist').DataTable({
            responsive: true,
            "bDestroy": true,
            data: data,
            scrollY: 500,
            "bDeferRender": true,
            columns: [
                { data: 'url' },
                { data: 'time' },
                { data: 'feq' },
                { data: 'count' },
                { data: 'last_time' },
                { data: 'del' },
                { data: 'more' },
                { data: 'update' }
            ]
        });
    }

    //initial already_exist table
    $.getJSON('/api_already_exist_data', {
        a: 1
    }, function(data) {
        refrsh_tables(data)
    });

    $('#add').bind('click', function() {
        title = $('input[name="title"]').val();
        keyword = $('input[name="keyword"]').val();
        abstract = $('input[name="abstract"]').val();
        author = $('input[name="author"]').val();
        insititution = $('input[name="insititution"]').val();
        begin = $('input[name="begin"]').val();
        end = $('input[name="end"]').val();
        time = $('select[name="times"]').val();
        if (title == '' && keyword == '' && abstract == '' && insititution == '' && author == '') {
            alert('内容作者不能同时为空！');
            return false
        }
        if (begin > end) {
            alert('起始年不能大于结束年！');
            return false
        }
        $.post('/api_paper_add_item', {
            title: title,
            keyword: keyword,
            abstract: abstract,
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

    //================refresh_task========================
    $('#already_exist').on('click', '#download', function() {
        var table = $('#already_exist').DataTable();
        var data = table.row($(this).parents('tr')).data()
        $('#log').html("");
        $('#log').append('<p>' + $('<div/>').text('任务开始：').html());
        log_socket(data['url']);

    });

    $('#already_exist').on('click', 'button.close', function() {
        if (confirm('确认要删除么？')) {
            var button = this
            var table = $('#already_exist').DataTable();
            var data = table.row($(this).parents('tr')).data();
            $.post('/api_paper_delete_task', {
                url: data['url']
            }, function(data) {
                if (data == 0) {
                    $('#already_exist').DataTable()
                        .row($(button).parents('tr'))
                        .remove()
                        .draw();
                    set_detail('head-detail', 'body-detail', [])
                    $('#paper_list').DataTable({
                        "bDestroy": true,
                        data: data,
                        scrollY: 500,
                        "bDeferRender": true,
                        columns: [
                            { data: "title" },
                            { data: "link" },
                            { data: "abstract" },
                            { data: "authors" },
                            { data: "date" },
                            { data: "spidertime" }

                        ]
                    });
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
            $.post('/api_paper_task_tr_click', {
                url: data['url']
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

    //modify task
    $('#modify_task').bind('click', function() {
        alert('你确定要修改么？');
        url_ = $('input[id="url"]').val();
        title = $('input[id="title"]').val();
        keyword = $('input[id="keyword"]').val();
        abstract = $('input[id="abstract"]').val();
        author = $('input[id="author"]').val();
        insititution = $('input[id="insititution"]').val();
        feq = $('select[id="feq"]').val();
        if (title == '' && keyword == '' && abstract == '' && insititution == '' && author == '') {
            alert('内容作者不能同时为空！');
            return false
        }
        $.post('/api_paper_modify_task', {
            url: url_,
            title: title,
            keyword: keyword,
            abstract: abstract,
            author: author,
            insititution: insititution,
            feq: feq
        }, function(data) {
            if (data == null) {
                alert("任务已存在，修改失败！");
            } else {
                $.getJSON('/api_already_exist_data', {
                    a: 1
                }, function(data) {
                    refrsh_tables(data)
                });
            }
        });
        return false;
    });

    //
    function set_detail(head_id, content) {
        document.getElementById('url').value = content['url'];
        document.getElementById('abstract').value = content['abstract'];
        document.getElementById('title').value = content['title'];
        document.getElementById('keyword').value = content['keyword'];
        document.getElementById('author').value = content['authors'];
        document.getElementById('insititution').value = content['insititution'];
        document.getElementById('feq').value = content['feq'];

    }

    //show task item detail
    $('#paper_list').DataTable({
        responsive: true,
        "scrollY": "300px",
        "bDeferRender": true,
        // data:data
    });



    $('#already_exist').on('click', '#more', function() {
        var table = $('#already_exist').DataTable();
        var data = table.row($(this).parents('tr')).data()
        if (data != null) {
            $.post('/api_paper_list', {
                url: data['url'],
            }, function(data) {
                if (!data) return;
                $('#paper_list').DataTable({
                    "bDestroy": true,
                    data: data,
                    scrollY: 500,
                    "bDeferRender": true,
                    columns: [
                        { data: "title" },
                        { data: "link" },
                        { data: "abstract" },
                        { data: "authors" },
                        { data: "date" },
                        { data: "spidertime" }

                    ]
                });

            });
        }

    });


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


    function log_socket(url) {
        //websocket配置
        console.log("dadfasd");
        namespace = '/runtime_log';

        // Connect to the Socket.IO server.
        // The connection URL has the following format:
        //     http[s]://<domain>:<port>[/<namespace>]
        console.log(connect_tag)
        if (!connect_tag) {
            socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {
                "reconnection": false,
                "force new connection": true,
                "autoconnect": true
            });
            connect_tag = true;
            socket.emit('connect');
            socket.emit('message',url)
            socket.on('my_response', function(msg) {
                $('#log').append('<p>' + $('<div/>').text('Received #' + msg.data).html());
                $('#log').scrollTop($('#log')[0].scrollHeight);
            });

            socket.on('disconnect', function(msg) {
                console.log()
                $('#log').append('<p>' + $('<div/>').text('断开连接!').html());
                $('#log').scrollTop($('#log')[0].scrollHeight);
                socket = null;
            });
        }

    }
    $('#disconnect').on('click', function() {
        connect_tag = false;
        socket.disconnect();

    });


});
