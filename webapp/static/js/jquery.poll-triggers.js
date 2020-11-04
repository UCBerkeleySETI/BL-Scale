$(function poll() {
    var message_sub = $('#pollScript').attr("current_state");
    queryString = "state="+message_sub;
    
    $.ajax({
        url:"/poll",
        data: queryString,
        timeout: 60000,
        success: function(change) {
            if(change == "change"){
                console.log("detected change");
                update();
            }
            console.log("did not detect change")
            poll();
        },
        error: function() {
            console.log("failed")
            window.location.href = 'login.html'
        }
    });
});

function update() {
    $.ajax({
        url:"/trigger",
        type:"GET",
        success: function(){
            console.log("updated trigger")
        }
    });
}