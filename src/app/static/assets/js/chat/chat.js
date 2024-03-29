/*-------------------- Start of Chat list and search logic  --------------------*/
_hasInappropriateLanguage = false;
let userList = [];
let prevChats = [];
const chatList = document.getElementById("chatList");

function processChats(chats, currentReceiverId) {
    userList = chats;

    // Keep track of the user IDs of the chats that are currently displayed in the chat list
    const displayedChats = new Set();
    
    // Check if the chats array has changed
    let chatsChanged = false;

    if (chats.length !== prevChats.length) {
        chatsChanged = true;
    } else {
        for (let i = 0; i < chats.length; i++) {
            const chat = chats[i];
            const prevChat = prevChats[i];
            if (
                // TODO Compare the last messaege here to see if it has changed
                chat._id !== prevChat._id ||
                chat.conversation_id !== prevChat.conversation_id ||
                chat.online !== prevChat.online ||
                chat.read !== prevChat.read ||
                chat.username !== prevChat.username ||
                chat.profile !== prevChat.profile ||
                chat.message_id !== prevChat.message_id
            ) {
                chatsChanged = true;
                break;
            }
        }
    }

    // Update the DOM if the chats array has changed
    if (chatsChanged) {
        // Update the chat list HTML
        let chatListHtml = "";
        for (let i = 0; i < chats.length; i++) {
            const chat = chats[i];
            chatListHtml += getChatHtml(chat, currentReceiverId, false);
            displayedChats.add(chat._id);
        }
        chatList.innerHTML = chatListHtml;

        // Remove chat list elements that are no longer displayed
        const chatElements = chatList.getElementsByTagName("a");
        for (let i = chatElements.length - 1; i >= 0; i--) {
            const element = chatElements[i];
            if (!displayedChats.has(element.id)) {
                element.remove();
            }
        }

        // Update the prevChats array
        prevChats = chats;
    }
}

function getOnlineStatusColour(online) {
    return online ? "bg-success" : "bg-secondary";
}

const receiverOnlineHeader = document.getElementById("receiverOnlineHeader");
const receiverProfileImage = document.getElementById("receiverProfileImage");
const receiverDisplayName = document.getElementById("receiverUsername"); // Display name is the username

function getChatHtml(chat, currentReceiverId, filteredFromSearch) {
    // TODO - If now no receiver is selected, select the current receiver id

    const online = `
    <div class="position-absolute bg-white p-1 rounded-circle bottom-0 end-0">
        <div class="${getOnlineStatusColour(chat.online)} rounded-circle w-3 h-3"></div>
    </div>`;

    // if the chat is the current receiver, 
    // also indicate the online status on the top of the page
    let bgColour = "hover:bg-gray-100";
    // note that _id is the user ID
    if (chat._id == currentReceiverId) {
        bgColour = "bg-light";

        if (receiverOnlineHeader.innerHTML != online) {
            receiverOnlineHeader.innerHTML = online;
        }

        // if (receiverProfileImage.src != chat.profile) {
        //     receiverProfileImage.src = chat.profile;
        // }
        
        if (receiverDisplayName.innerText != chat.display_name) {
            // NOTE: We can use innerHtml here as it is already escaped by the server
            receiverDisplayName.innerHtml = chat.display_name;

            // update all the messages sent by this user with the new display name
            const chatMessages = document.getElementsByClassName("message-receiver");
            for (let i = 0; i < chatMessages.length; i++) {
                const chatMessage = chatMessages[i];
                if (chatMessage.innerText != chat.display_name) {
                    chatMessage.innerHtml = chat.display_name;
                }
            }
        }
    }

    // reduce the message to 20 characters
    var chatMsg = (chat.message.length > 10) ? chat.message.slice(0, 10) + "..." : chat.message;
    if (chatMsg.trim().split(":")[1].trim() === "") {
        chatMsg = "";
    }

    var redirectUrl = `/chat/${chat.username}`;

    return chatHtml = `
        <a id="${chat._id}" href="${redirectUrl}" class="d-flex align-items-center">
            <div class="flex-shrink-0">
                <img class="img-fluid" src="${chat.profile}" alt="user img" style="width: 40px; height 40px;">
                <span class="active"></span>
            </div>
            <div class="flex-grow-1 ms-3">
                <h3>${chat.username}</h3>
                <div style="display:flex">
                <p class="text-muted">${chatMsg}</p>
                <p class="ms-2" data-chatlist-timestamp="${chat.timestamp}"></p>
                </div>
            </div>
        </a>
    `;
}

setInterval(() => {
    const readableTimes = document.querySelectorAll("[data-chatlist-timestamp]");
    for (const readableTime of readableTimes) {
        const sendTime = readableTime.getAttribute("data-chatlist-timestamp");
        if (sendTime === null || sendTime === undefined || sendTime === "") {
            readableTime.innerText = "";
            continue;
        }
        const timestamp = new Date(sendTime).getTime();
        readableTime.innerText = getReadableTimeDiff(timestamp);
    }
}, 500);
setInterval(() => {
    const chatTimestamps = document.querySelectorAll("[data-chat-timestamp]");
    for (const chatTimestamp of chatTimestamps) {
        const timestamp = chatTimestamp.getAttribute("data-chat-timestamp");
        chatTimestamp.innerText = formatDateTime(timestamp);
    }
}, 5000);
/*-------------------- End of Chat list and search logic  --------------------*/

/*-------------------- Start of functions used by the chat websocket  --------------------*/

const mainMsgDiv = document.getElementById("mainMsgDiv");
const messageArea = document.getElementById("chatArea");
const inputMsg = document.getElementById("messageText");
let conversationId = document.getElementById("conversationId");
// let _hasInappropriateLanguage = false;

function getReadableFileSize(nBytes) {
    var i = nBytes == 0 ? 0 : Math.floor(Math.log(nBytes) / Math.log(1024));
    return (nBytes / Math.pow(1024, i)).toFixed(2) * 1 + " " + ["B", "kB", "MB", "GB", "TB"][i];
}

async function sendMessage(ws, event) {
    event.preventDefault();

    // strip value of whitespace
    inputMsg.value = inputMsg.value.trim();
    lastMsg = inputMsg.value;

    // if the value is empty, don't send
    if (inputMsg.value == "") {
        return;
    }

    // Check if the message has inappropriate language
    const messageData = {
        message: inputMsg.value,
    };

    const _hasInappropriateLanguage = await detectToxicity(messageData)
    if (!_hasInappropriateLanguage) {
        console.log("THEN: No inappropriate language detected");

        // Send the JSON message
        const data = {
            message: inputMsg.value,
            // Get the conversation from the current selected receiver
            conversation_id: conversationId.value,
        };
        console.log(data);
        console.log(ws);
        ws.send(JSON.stringify(data));
    } 
    
    inputMsg.value = "";
    // chatMsgFileTextInput.value = "";
    event.preventDefault();
};

function deleteMessage(ws, messageId) {
    const data = {
        delete: messageId,
    };
    ws.send(JSON.stringify(data));
    const msgDiv = document.getElementById(messageId);
    if (msgDiv) {
        msgDiv.remove();
    }
}

async function detectToxicity(messageData) {
    try {
        const response = await fetch("/api/chat/detect_toxicity", {
            method: "POST",
            body: JSON.stringify(messageData),
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }

        const data = await response.json();
        if (data.message) {
            Swal.fire({
                title: 'warning!',
                text: data.message,
                icon: 'warning',
                confirmButtonText: 'Okay'
            });
            return true;
        }
        return false
    } catch (error) {
        console.error("Error:", error);
    } finally {
        console.log("hasInappropriateLanguage: ", _hasInappropriateLanguage);
    }
}

/*-------------------- End of functions used by the chat websocket  --------------------*/