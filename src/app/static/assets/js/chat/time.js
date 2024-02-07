// For Chatlist Time: Format the time difference between the current time and a given timestamp into a human-readable string
function getReadableTimeDiff(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    const diffDays = Math.floor(diff / (1000 * 3600 * 24));
    const diffHours = Math.floor(diff / (1000 * 3600));
    const diffMinutes = Math.floor(diff / (1000 * 60));
    const diffSeconds = Math.floor(diff / 1000);

    if (diffDays > 3) {
        return date.toLocaleDateString("en-US");
    } else if (diffDays > 0) {
        return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;
    } else if (diffHours > 0) {
        return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
    } else if (diffMinutes > 0) {
        return `${diffMinutes} minute${diffMinutes > 1 ? "s" : ""} ago`;
    } else {
        return "Just now";
    }
}

// For Chat Time: Format a given date and time string into a human-readable string
function formatDateTime(dateTimeStr) {
    // Parse the input string into a Date object
    const msgDate = new Date(dateTimeStr);
    // Get the current date and time
    const now = new Date();
    
    // Check if the message date is today by comparing day, month, and year
    const isToday = msgDate.getDate() === now.getDate() &&
                    msgDate.getMonth() === now.getMonth() &&
                    msgDate.getFullYear() === now.getFullYear();

    // Format the hour and minute
    let hours = msgDate.getHours();
    const minutes = msgDate.getMinutes();
    // Determine AM or PM
    const ampm = hours >= 12 ? 'PM' : 'AM';
    // Convert hour from 24-hour to 12-hour format
    hours = hours % 12;
    hours = hours ? hours : 12; // Convert 0 hours to 12 for 12-hour clock
    // Ensure minutes are two digits
    const minutesStr = minutes < 10 ? '0' + minutes : minutes;

    // Return the formatted string based on whether the date is today
    if (isToday) {
        // If it's today, return the time in hh:mm AM/PM format
        return `${hours}:${minutesStr} ${ampm}`;
    } else {
        // If it's not today, return the date in DD/MM/YYYY format, followed by the time
        const day = msgDate.getDate() < 10 ? '0' + msgDate.getDate() : msgDate.getDate();
        const month = msgDate.getMonth() + 1 < 10 ? '0' + (msgDate.getMonth() + 1) : msgDate.getMonth() + 1; // Months are zero-indexed
        const year = msgDate.getFullYear();
        return `${day}/${month}/${year}, ${hours}:${minutesStr} ${ampm}`;
    }
}