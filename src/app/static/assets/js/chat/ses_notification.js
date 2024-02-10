// Send email when message is sent and recevier is not online
function sendTextNotificationMail(){
    var receiver_status = document.getElementById('receiverOnlineHeader').innerText;
    if(receiver_status == "Offline"){
        var receiver = document.getElementById("receiverUsername").innerText;
        var message =  document.getElementById('messageText').value;
        var sender = document.getElementById("current_username").innerText;
        const formData = {Sender:sender,Receiver:receiver,Message:message};
        fetch("/sendNotificationTextEmail", {
            method: "POST",
            body: JSON.stringify(formData),
            headers: {
                "Content-Type": "application/json",
        },
        })
        .then((response) => response.json())
        .then((data) => {
            console.log(data)
        })
    }
}