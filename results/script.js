String.prototype.format = function() {
    var s = this;
    var i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

function sortByMaxValue(A, B) {
    return A.data[A.data.length-1][1] < B.data[B.data.length-1][1] ? 1 : -1;
}

function formatNumber(num, axis){
    if (num < 1000)
        return Math.round(num * 1000) / 1000;
    var n = num.toString(), p = n.indexOf('.');
    return n.replace(/\d(?=(?:\d{3})+(?:\.|$))/g, function($0, i){
        return p<0 || i<p ? ($0+',') : $0;
    });
}

function loadData(datasets) {

    // hard-code color indices to prevent them from shifting as
    // items are turned on/off

    var i = 0;
    $.each(datasets, function(key, val) {
        val.color = i++;
    });

    var keys = Object.keys(datasets);
    keys.sort(function(a,b) {
        return sortByMaxValue(datasets[a], datasets[b]);
    });

    // insert checkboxes 
    var choiceContainer = $("#choices");
    $.each(keys, function(idx) {
        var key = keys[idx];
        var val = datasets[key];
        choiceContainer.append(
            "<br/><input type='checkbox' name='{0}' checked='checked' id='id{0}'></input><label for='id{0}'>{1}</label>".format(key, val.label)
        );
    });

    choiceContainer.find("input").click(function() {
        plotAccordingToChoices(datasets);
    });

    plotAccordingToChoices(datasets);
}

function plotAccordingToChoices(datasets) {

    var data = [];

    $("#choices").find("input:checked").each(function () {
        var key = $(this).attr("name");
        if (key && datasets[key]) {
            data.push(datasets[key]);
        }
    });

    // Sort data by max value
    data.sort(sortByMaxValue);

    if (data.length > 0) {
        $.plot("#placeholder", data, {
            yaxis: {
                min: 0,
                tickFormatter: formatNumber
            },
            xaxis: {
                tickDecimals: 0,
                tickFormatter: formatNumber
            },
            grid: {
                hoverable: true
            },
            tooltip: {
                show: true
            },
            series: {
                lines: {
                    show: true
                },
                points: {
                    show: true
                }
            },
        });
    }
}
