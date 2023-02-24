const mid=JSON.parse(document.getElementById("mid").textContent)
const id=JSON.parse(document.getElementById("id").textContent)
let inter;
let timmer=document.querySelector("#timmer")
function startTimmer(){
    let sec=120;
    inter=setInterval(() => {
        timmer.innerHTML=`${parseInt(sec/60)}:${sec%60}`
        if(sec===0){
            clearInterval(inter);
            location.href="/cancel"
        }
        sec-=1
    }, 1000);
}

let clientStatus=JSON.parse(document.getElementById("status").textContent)
    if(clientStatus==="host"){
    //    window.open(`/meetingarea/?id=${mid}","",'fullscreen=yes,titlebar=no,toolbar=no,statusbar=no`)
       location.href = `/meetingarea/?id=${mid}`
   }
   else
   {
       let socket = new WebSocket(`ws://${location.host}/ws/waitingroom/`)
       socket.onopen = () => socket.send(JSON.stringify({mid: mid, id: id}))
       startTimmer()
       socket.onmessage = function (event) {
           let response=JSON.parse(event.data)
           let action=response['action']
           if(action==="request"){
           let status = response['request_status']
           if (status) {
            //    window.open(, "1300", "700")
               location.href = `/meetingarea/?id=${mid}`
           } else {
               alert("Host Not accept Your Request")
               setTimeout(()=>{
               location.href = "/cancel/"
               },3000)
           }}
           else if(action==="host_left"){
               alert("Host End The Meeting")
               setTimeout(()=>{

               location.href="/cancel/"
               },3000)
           }
       }
      
   }