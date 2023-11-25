// "use strict";

// var notificationConnection = new signalR.HubConnectionBuilder().withUrl("/notificationHub").build();

// notificationConnection.on("ReceiveNotification", function (notification) {
//   var noNotif = document.getElementById("noNotification");
//   if (noNotif != null) {
//     noNotif.remove();
//   }
//   console.log(notification);
//   let { id, message, system, date, read } = notification;
//   var tableBody = document.getElementById('tableBody');
//   var row = document.createElement('tr');
//   tableBody.appendChild(row);
//   row.id = "notification_" + id;
//   var sysCol = document.createElement('td');
//   row.appendChild(sysCol);
//   sysCol.textContent = system;
//   var msgCol = document.createElement('td');
//   row.appendChild(msgCol);
//   msgCol.textContent = message;
//   var readCol = document.createElement('td');
//   row.appendChild(readCol);
//   readCol.textContent = read ? "Read" : "Unread";
//   var dateCol = document.createElement('td');
//   row.appendChild(dateCol);
//   dateCol.textContent = date;
//   var actionCol = document.createElement('td');
//   row.appendChild(actionCol);
//   actionCol.textContent = "-";

//   var total = document.getElementById('totalNotifications')
//   var tnum = parseInt(total.innerText)
//   total.innerText = tnum + 1
//   var unread = document.getElementById('unreadNotifications')
//   var unum = parseInt(unread.innerText)
//   unread.innerText = unum + 1
// });

// notificationConnection.on("ReceiveNotificationCount", function (count) {
//   var counter = document.getElementById("notificationCount");
//   counter.innerText = count;
// });

// function deleteNotification(e) {
//   var row = e.parentElement.parentElement;
//   let { id } = row;
//   var notificationId = id.split("_")[1]
//   notificationConnection.invoke("DeleteNotification", parseInt(notificationId)).catch(err => console.log(err));
//   row.remove();
//   var total = document.getElementById('totalNotifications')
//   var tnum = parseInt(total.innerText)
//   total.innerText = tnum - 1

//   if (parseInt(total.innerText) == 0) {
//     var tableBody = document.getElementById('tableBody');
//     var noNotif = document.createElement('tr');
//     tableBody.appendChild(noNotif)
//     noNotif.id = "noNotification";
//     var innerMsg = document.createElement('td');
//     noNotif.appendChild(innerMsg)
//     innerMsg.colSpan = 5;
//     innerMsg.textContent = "No notifications yet."
//   }
// }

// function readNotification(e) {
//   let { id: idPackage } = e;
//   var id = parseInt(idPackage.split("_")[1]);
//   notificationConnection.invoke("ReadNotification", id)
//     .then(() => {
//       var row = document.getElementById(`notificationActions_${id}`);
//       var newButton = document.createElement('button');
//       row.appendChild(newButton);
//       newButton.className = "btn"
//       var icon = document.createElement('i');
//       newButton.appendChild(icon);
//       icon.className = "fa fa-trash";
//       newButton.addEventListener('click', () => deleteNotification(newButton))
//       var readCol = document.getElementById(`notificationRead_${id}`);
//       readCol.innerText = "Read"
//       var unread = document.getElementById('unreadNotifications')
//       var unum = parseInt(unread.innerText)
//       unread.innerText = unum - 1
//     })
//     .catch(err => console.log(err))
// }

// async function start() {
//   try {
//     await notificationConnection.start();
//     console.log("SignalR Connected.");
//   } catch (err) {
//     console.log(err);
//     setTimeout(start, 5000);
//   }
// }

// notificationConnection.onclose(async () => {
//   await start();
// });

// // Start the connection.
// start();