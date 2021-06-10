
const btn = document.getElementById("sub");
btn.innerText = "submit"
btn.addEventListener("click", onSubmt)


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

    const name = document.getElementById("name").value
    const email = document.getElementById("email").value
    const branch = document.getElementById("branch").value
    const year = document.getElementById("year").value
    const password = document.getElementById("password").value

    // console.log(base64)
    console.log(email)


    axios.post("http://127.0.0.1:5000/api/student/register", {
        name: name,
        email: email,
        branch: branch,
        year: year,
        password: password,
        image: base64
    }).then((res) => {
        const span = document.createElement("span")
        span.innerHTML = res.data.message
        document.body.append(span)
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



