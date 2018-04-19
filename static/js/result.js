$(function() {
    console.log( "result ready!" );
    ratio_list = [windows_ratio, office_ratio, sql_ratio];
    green_data = [];
    red_data = [];
    yellow_data = [];

    for(var i = 0; i < ratio_list.length; i++){
        ratio = ratio_list[i];
        if(ratio > 0.7){
            green_data.push([i+1,ratio]);
        } else if (ratio > 0.4) {
            yellow_data.push([i+1,ratio]);
        } else {
            red_data.push([i+1,ratio]);
        }
    }
    
    var chart_data = [{data: red_data, color: "red"},
                      {data: yellow_data, color: "yellow"},
                      {data: green_data, color: "green"}];

    $.plot("#flotMAP", chart_data, {
        series: {
            bars: {
                show: true,
                barWidth: 0.6,
                align: "center"
            }
        },
        yaxis: {
            tickLength:0
        },
        xaxis: {
            tickLength:0,
            axisLabelPadding: 5,
            min: 0,
            max: 4,
            ticks:[[1,'Windows'],[2,'Office'],[3,'SQL Server']]
        }
    });
});