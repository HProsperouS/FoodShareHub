// "use strict";

// var chatConnection = new signalR.HubConnectionBuilder().withUrl("/householdHub").build();


// //Disable the send button until connection is established.
// document.getElementById("sendButton").disabled = true;

// chatConnection.on("ReceiveMessage", function (messageViewModel) {
//   let { key: id, username: userName, message, createdAt: time, imagePath } = messageViewModel;
//   var isUser = document.getElementById("username").value == userName
//   console.log(userName)
//   console.log(document.getElementById("username").value)
//   var container = document.createElement("div");
//   document.getElementById("messagesList").appendChild(container);
//   // We can assign user-supplied strings to an element's textContent because it
//   // is not interpreted as markup. If you're assigning in any other way, you
//   // should be aware of possible script injection concerns.
//   container.className = !isUser ? "text-white px-2 rounded" : "px-2 border rounded ms-auto";
//   container.style = !isUser ? "background-color: #33764e;" : "";
//   container.id = `message_${id}`;
//   if (imagePath != null) {
//     var img = document.createElement('img');
//     container.appendChild(img);
//     img.src = "/" + imagePath;
//     img.width = 400;
//     img.height = 300;
//     img.style.objectFit = "cover";
//     img.loading = "lazy";
//   }
//   var nameAndTrashRow = document.createElement("div");
//   container.appendChild(nameAndTrashRow);
//   nameAndTrashRow.className = "d-flex justify-content-between align-items-center"
//   var userNameText = document.createElement("strong");
//   nameAndTrashRow.appendChild(userNameText);
//   userNameText.textContent = userName;
//   if (isUser) {
//     var trashIcon = document.createElement("i");
//     nameAndTrashRow.appendChild(trashIcon);
//     trashIcon.className = "fa fa-trash";
//     trashIcon.addEventListener('click', (e) => deleteMessage(trashIcon))
//   }
//   var messageBody = document.createElement("div");
//   container.appendChild(messageBody);
//   messageBody.className = "d-flex gap-3"
//   var messageText = document.createElement("p");
//   messageBody.appendChild(messageText)
//   messageText.textContent = message;
//   messageText.className = !isUser ? "text-white" : "";
//   var messageTime = document.createElement("small");
//   messageBody.appendChild(messageTime);
//   messageTime.textContent = time;
//   messageTime.className = "small text-muted";

//   var messageList = document.getElementById("messagesList");
//   messageList.scrollTop = messageList.scrollHeight;
// });

// chatConnection.on("ReceiveDeleteMessage", function (messageId) {
//   console.log(`Received instruction to delete message_${messageId}`);
//   document.getElementById(`message_${messageId}`).remove();
// })

// chatConnection.start().then(function () {
//   document.getElementById("sendButton").disabled = false;
//   chatConnection.invoke("JoinGroup", document.getElementById("householdId").value)
//     .catch(err => console.log(err))
// }).catch(function (err) {
//   return console.error(err.toString());
// });

// function deleteMessage(e) {
//   var id = e.parentElement.parentElement.id;
//   var messageId = id.split("_")[1]
//   chatConnection.invoke("DeleteMessage", messageId).catch(function (err) {
//     return console.error(err.toString());
//   })
// }

// async function sendMessage() {
//   const toBase64 = file => new Promise((resolve, reject) => {
//     const reader = new FileReader();
//     reader.readAsDataURL(file);
//     reader.onload = () => resolve(reader.result);
//     reader.onerror = error => reject(error);
//   });

//   var messageInput = document.getElementById("messageInput");
//   var fileInput = document.getElementById("fileInput")
//   var userId = document.getElementById("userId").value;
//   var text = messageInput.value;
//   if (text == "") {
//     return;
//   }
//   var base64Image = null
//   if (fileInput.files.length != 0) {
//     base64Image = await toBase64(fileInput.files[0])
//   }
//   messageInput.value = "";
//   fileInput.value = "";
//   if (base64Image != null) {
//     chatConnection.invoke("SendMessageWithImage", userId, text, base64Image).catch(function (err) {
//       return console.error(err.toString());
//     });
//   }
//   else {
//     chatConnection.invoke("SendMessage", userId, text).catch(function (err) {
//       return console.error(err.toString());
//     });
//   }
// }

// document.getElementById("messageForm").addEventListener("submit", async (e) => {
//   e.preventDefault();
//   await sendMessage();
// })