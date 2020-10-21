$('#switch').change(function(){
    //call the endpoint to switch the production mode
    console.log("switched toggle")
    $.ajax({
        url:"/toggle-server",
        success: function(change) {
            console.log("changed to " + change + " mode.")
        },
        error: function() {
            console.log("failed to change server.")
        }
    });
});