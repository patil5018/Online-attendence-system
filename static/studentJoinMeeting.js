
const btn = document.getElementById("sub1");
btn.innerText = "Start Attending"
btn.addEventListener("click", registerMeeting)

function registerMeeting() {
    // /api/student/register_to_meeting

    const capture = document.createElement("canvas")
    var ctx = capture.getContext('2d')
    var img = new Image()

    ctx.drawImage(video, 0, 0, capture.width, capture.height);

    img.src = capture.toDataURL("image/png");
    img.width = 300;
    img.height = 300;
    const imgURL = capture.toDataURL("image/png");
    const base64 = imgURL.replace(/^data:image\/(png|jpg);base64,/, "");

    const meetingId = document.getElementById("meetingid").value

    axios.post("http://127.0.0.1:5000/api/student/register_to_meeting", {
        meetingid: meetingId,
        image: base64
    }).then((res) => {
        // console.log(res.data)
        if (res.data.message === "registered for meeting") {
            let count = 0

            let timeOut = 1000 * 3   //1000 * 60 * 5

            let timer = setInterval(() => {
                if (count < 12) {
                    count++;
                    // console.log(count)
                    verifyAttendence(meetingId, base64)
                } else {
                    clearInterval(timer)
                }
            },
                timeOut)
        } else {
            console.log("you cant join the meeting")
            console.log("reason :: " + res.data.message)
        }
    })
}


function verifyAttendence(meetingId, image) {
    axios.post("http://127.0.0.1:5000/api/student/attend", {
        meetingid: meetingId,
        image: image
    }).then((res) => {
        console.log(res.data.message)
    })
}


//document.getElementById("formOne").appendChild(btn)

function onSubmt() {

    const capture = document.createElement("canvas")
    var ctx = capture.getContext('2d')
    var img = new Image()

    ctx.drawImage(video, 0, 0, capture.width, capture.height);

    img.src = capture.toDataURL("image/png");
    img.width = 300;
    img.height = 300;
    const imgURL = capture.toDataURL("image/png");
    const base64 = imgURL.replace(/^data:image\/(png|jpg);base64,/, "");

    const meetingid = document.getElementById("meetingid").value

    // console.log(base64)


    axios.post("http://127.0.0.1:5000/api/student/register", {
        meetingid: meetingid,
        image: base64
    }).then((res) => {
        // const span = document.createElement("span")
        // span.innerHTML = res.data.message
        // document.body.append(span)
        console.log(res.data)
    })
}



var video = document.getElementById('video');

// Get access to the camera!
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    // Not adding `{ audio: true }` since we only want video now
    navigator.mediaDevices.getUserMedia({ video: true }).then(function (stream) {
        //video.src = window.URL.createObjectURL(stream);
        video.srcObject = stream;
        video.play();
    });
}



