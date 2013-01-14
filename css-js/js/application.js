
$('.form_popover').popover({ 
    html : true,
    placement: 'left',
    title: function() {
        return $("#formPopClassTitle").html();
    },
    content: function() {
        return $("#formPopClassForm").html();
    }
});

$(function () {
    Object.size = function(obj){
        var size = 0, key;
        for(key in obj){
            if(obj.hasOwnProperty(key)) size++;
        }
        return size;
    };

    var text = $("#chart_data").html();
    var myObject = JSON.parse(text);

    var size = Object.size(myObject);
    var d1 = [];

    for(var i=0; i<size; i++)
        d1.push([Date.parse(myObject[i].Date), parseFloat(myObject[i].Close)]);

    var new_plot = $.plot($("#chart"), [d1], {
        xaxis: {
            mode: "time",
            timeformat: "%y/%m/%d"
        }
    });
});
