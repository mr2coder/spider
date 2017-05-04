$(document).ready(function() {
    num = 1;
    myChart = echarts.init(document.getElementById('body-graph'));

    function refrsh_tables(data) {
        var data = data;
        for (var i = 0; i < data.length; i++) {
            if (data[i]['status'] == 0) {
                data[i]['del'] = "已完成"
            } else {
                data[i]['del'] = '<button type="button" style="float: left;" name="close" class="close" data-dismiss="alert">' + '<span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>';

            }
            data[i]['more'] = '<button type="button" style="float: left;" name="more" class="more" data-dismiss="alert" >' + '<span class="glyphicon glyphicon-stats"  aria-hidden="true"></span></button>';
            data[i]['update'] = '<button type="button" style="float: left;" id="download" name="download" class="more" data-toggle="modal" data-target="#paperModal"><span class="glyphicon glyphicon-refresh" aria-hidden="true"></span></button>';
            if (data[i]['inactive'] == 1) {
                data[i]['inactive'] = '是'
            } else {
                data[i]['inactive'] = '否'
            }
        }
        $('#already_exist').DataTable({
            responsive: true,
            "bDestroy": true,
            data: data,
            scrollY: 335,
            "bDeferRender": true,
            columns: [
                { data: 'content' },
                { data: 'site' },
                { data: 'time' },
                { data: 'feq' },
                { data: 'last_time' },
                { data: 'inactive' },
                { data: 'del' },
                { data: 'more' },
                { data: 'update' }

            ]
        });
    }
    //get initial data of the table
    $.getJSON('/api_video_initial_spider', {
        a: 1
    }, function(data) {
        refrsh_tables(data)
    });


    $('#video_list').DataTable({
        responsive: true,
        "scrollY": "300px",
        "bDeferRender": true,
        // data:data
    });



    $('#add').bind('click', function() {
        content = $('input[name="content"]').val();
        site = $('select[name="site"]').val();
        feq = $('select[name="feq"]').val();
        len = $('select[name="len"]').val();
        time_limit = $('select[name="time_limit"]').val();

        site = JSON.stringify(site)
        if (content == '') {
            alert('内容不能为空！');
            return false
        }
        $.post('/api_add_video_spider', {
            content: content,
            site: site,
            feq: feq,
            len: len,
            time_limit: time_limit
        }, function(data) {
            if (data == null) {
                alert("任务已存在，请不要重复添加！")
                return false
            }
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
            // console.log(data);
            $.post('/api_video_delete_task', {
                site: data['site'],
                content: data['content'],
                time: data['time']
            }, function(data) {
                if (data == 0) {
                    $('#already_exist').DataTable()
                        .row($(button).parents('tr'))
                        .remove()
                        .draw();
                    set_detail('head-detail', 'body-detail', [])
                } else {
                    alert('删除失败');
                }

            });
        }
    });

    $('#video_list tbody').on('click', 'button.more', function() {
        var table = $('#video_list').DataTable();
        var data = table.row($(this).parents('tr')).data()
            // console.log(data)
            // $.getJSON('/api_play_info', {
            //         videoname : data['videoname']
            //     }, function(data) {

        //     });
        var myPlayer = videojs('example_video_1', {
            "controls": true,
            "length": 400,
            "width": 600,
            "preload": "no",
            "data-setup": "{}"
        });
        var story_sources = [{
            type: "video/flv",
            src: "static/video/" + data['videoname'] + ".flv"
        }];
        myPlayer.ready(function() {
            var obj = this;
            obj.src(story_sources);
            obj.load();
        });

        $('#myModal').on('hide.bs.modal', function(e) {
            var oldPlayer = videojs(document.getElementById('example_video_1'));
            oldPlayer.dispose();
            document.getElementById("play_content").innerHTML = '<video id="example_video_1" class="video-js vjs-default-skin vjs-big-play-centered"></video>'
        })

    });




    //more button
    $('#already_exist').on('click', 'button.more', function() {
        var table = $('#already_exist').DataTable();
        var data = table.row($(this).parents('tr')).data()
            // console.log(data != null)
        if (data != null) {
            $.getJSON('/api_video_detail', {
                content: data['content'],
                site: data['site']
            }, function(data) {
                set_detail('head-detail', 'body-detail', data['info'])
            });
        }

    });
    //gragh set
    $('#already_exist').on('click', 'tr', function() {
        var table = $('#already_exist').DataTable();
        var data = table.row(this).data()
            // console.log(data != null)
        if (data != null) {
            $.getJSON('/api_video_gragh', {
                content: data['content'],
                site: data['site']
            }, function(data) {
                set_gragh('head-graph', data['content'], data['xy_value'])
            });
        }

    });

    $(window).resize(function() {
        myChart.resize();
    });

    function set_detail(head_id, body_id, content) {
        for (var i = 0; i < content.length; i++) {
            if (content[i]['status'] != 0) {
                content[i]['more'] = "未下载"
            } else {
                // content[i]['more'] = "未下载"
                content[i]['more'] = '<button type="button" style="float: left;" class="more" data-toggle="modal" data-target="#myModal"><span class="glyphicon glyphicon-play" aria-hidden="true"></span></button>';

            }
        }
        $('#video_list').DataTable({
            "bDestroy": true,
            data: content,
            scrollY: 500,
            "bDeferRender": true,
            columns: [
                { data: "videoname" },
                { data: "showtime" },
                { data: "videoinfo" },
                { data: "spidertime" },
                { data: "playtimes" },
                { data: "more" }

            ]
        });
    }

    function set_gragh(head_id, content, xy_value) {
        // console.log(content)
        document.getElementById('head-graph').innerHTML = '<span class="glyphicon glyphicon-sort"></span>  任务' + content + '抓取数量趋势'
            //初始化图表
            // 基于准备好的dom，初始化echarts图表
            // var myChart = echarts.init(document.getElementById('body-detail'));
        var option = {
            title: {
                text: '最近爬虫数量变化',
                subtext: ''
            },
            tooltsite: {
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
                // max: 5000,
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

    var socket = null;
    var connect_tag = false;

    $('#already_exist').on('click', '#download', function() {
        var table = $('#already_exist').DataTable();
        var data = table.row($(this).parents('tr')).data()
            //download button action
        console.log(data);
        $('#log').html("");
        $('#log').append('<p>' + $('<div/>').text('task begin...').html());
        log_socket(data['content'], data['site'])

    });

    function log_socket(content, site) {
        //websocket配置
        namespace = '/video';

        // Connect to the Socket.IO server.
        // The connection URL has the following format:
        //     http[s]://<domain>:<port>[/<namespace>]
        if (!connect_tag) {
            socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {
                "reconnection": false,
                "force new connection": true,
                "autoconnect": true
            });
            connect_tag = true;
            socket.emit('connect');
            socket.emit('message', content, site)
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

    /***
    弃用
    ***
    function refresh_log(url) {
        // body...
        $.post('/api_video_refresh_log', {
            url: url
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
        $.post('/api_video_download_end', {}, function(data) {
            // console.log(data)
            if (data == 0) {
                window.clearInterval(refresh_task);
                refresh_task = null;
                $('#log').append('<p>' + $('<div/>').text('task should be shutdown...').html());
                $('#log').scrollTop($('#log')[0].scrollHeight); //Keep the bottom alignment
            }
        });

    }
    */

});
