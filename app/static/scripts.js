var monday, tuesday, wednesday, thursday, friday, saturday, sunday;
function generateGridLists() {
    // monday = $("#monday").children();
    // // console.log(monday
    // tuesday = $("#tuesday").children();
    // wednesday = $("#wednesday").children();
    // thursday = $("#thursday").children(); //list of all input elements
    // friday = $("#friday").children();
    // saturday = $("#saturday").children();
    // sunday = $("#sunday").children();
    monday = $("#monday")
    tuesday = $("#tuesday")
    wednesday = $("#wednesday")
    thursday = $("#thursday") //list of all input elements
    friday = $("#friday")
    saturday = $("#saturday")
    sunday = $("#sunday")
}

function timeInMinutes(time) {
    timeArray = time.split(":");
    minutes = parseInt(timeArray[1]);
    minutes += 60 * parseInt(timeArray[0]);
    return minutes;
}


// console.log(monday);
function addEvent(start, end, day, name) {
    if(day == 0){
        var temp = monday;
    }else if(day == 1){
        var temp = tuesday;
    }else if(day == 2){
        var temp = wednesday;
    }else if(day == 3){
        var temp = thursday;
    }else if(day == 4){
        var temp = friday;
    }else if(day == 5){
        var temp = saturday;
    }else{
        var temp = sunday;
    }
    let startTime = timeInMinutes(start);
    let endTime = timeInMinutes(end);

    $(temp[startTime]).attr('class', 'grid-item-top');
    // $(monday[startTime-1]).html(name + "<br>" + startTime + " to " + endTime);
    $(temp[startTime]).html(name + ": " + start + " to " + end);
    for (var i = startTime+1; i < endTime-1; i++) {
        console.log(temp[i]);
        $(temp[i]).attr('class', 'grid-item-middle');
    }
    $(temp[endTime-1]).attr('class', 'grid-item-bottom');
}

// events should be a json file of all the events in on a particular day in sorted order by start time
function createDay(events, day, user, calendarName) {
    var temp;
    if(day == 0){
        temp = monday;
    }else if(day == 1){
        temp = tuesday;
    }else if(day == 2){
        temp = wednesday;
    }else if(day == 3){
        temp = thursday;
    }else if(day == 4){
        temp = friday;
    }else if(day == 5){
        temp = saturday;
    }else{
        temp = sunday;
    }

    var previous = 0;
    for (let key in events) { 
        let e = events[key];
        console.log(e);
        let start = timeInMinutes(e['start_time']);
        let end = timeInMinutes(e['end_time']);
        let eventHeight = end - start;
        let breakHeight = start - previous;
        let name = e['name'] + "<br>" + e['start_time'].substring(0,5) + " - " + e['end_time'].substring(0,5);
        let name2 = e['name'];
        temp.append("<div style='height:" + breakHeight + "px;' class='grid-item'></div>");
        let link = "'/calendars/" + e['eventid'] + "'";
        // temp.append("<a href= " + link + ">" + "<div style='height:" + eventHeight + "px;' class='grid-item'></div></a>");
        if (eventHeight >= 60)
        temp.append("<a href= " + link + "><div style='height:" + eventHeight + "px;' class='grid-item-event'>" + name + "</div></a>");
        else if (eventHeight <= 60 && eventHeight >= 30)
        temp.append("<a href= " + link + "><div style='height:" + eventHeight + "px;' class='grid-item-event'>" + name2 + "</div></a>");
        else
        temp.append("<a href= " + link + "><div style='height:" + eventHeight + "px;' class='grid-item-event'></div></a>");
        // console.log("href='/calendars/" + user + "/" + calendarName + "/" + e['eventid'] + "'");
        previous = end;
    }
    console.log(previous);
    var keys = Object.keys(events);
    console.log(keys.at(-1));
    // if 
    let breakHeight = 1440 - previous;
    temp.append("<div style='height:" + breakHeight + "px;' class='grid-item'></div>");
}