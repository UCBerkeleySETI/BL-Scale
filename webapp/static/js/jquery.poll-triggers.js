$(function poll() {

    queryString = "state="+JSON.stringify(message_sub);
    
    $.ajax({
        url:"/poll",
        data: queryString,
        timeout: 60000,
        success: function() {
            console.log("detected change");
            update();
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