
function handleServerMessage(event){
        let response=JSON.parse(event.data)
        let action=response['action']
        if(action==="entry") {
            let data=response['data']
            createNotification(data['name'],data['id'])
        }
        else if(action==="cancel_request"){
            deleteNotification(response["id"])
        }
        else if(action==="add_user"){
            addUser(response['name'],response['id'])
        }
        else if(action==="host_left"){
            alert("Meeting End By Host")
            setTimeout(()=>{
            location.href="/leave/"
            },3000)
        }
        else if(action==="block"){
            addUserNotification(`You Blocked By Host At ${new Date().toUTCString()} Now You can't communicate with others you message send to host only not other's`)
        }
        else if(action==="unblock"){
            addUserNotification(`You Are UnBlock By Host At ${new Date().toUTCString()}`)
        }
        else if(action==="user_left"){
            leftUser(response['name'])
            deleteUser(response["id"])
        }
        else if(action==="leave"){
            alert("Host Remove You")
            setTimeout(()=>{
            document.getElementById("leave-meeting").click()
            },2000)
        }
        else if(action==="message"){
            if(response['id']===id){
            let div=createMessage("You",response['msg'],response['date'],"")
                div.style.float="right"
                div.style.clear="both"
            }
        else{
             let div=createMessage(response['name'],response['msg'],response['date'],`( id  ${response['id']})`)
                div.style.float="left"
                div.style.clear="both"
            }
        message_area.scrollTo(0,message_area.scrollHeight)
        }
        else{

        }
    }

function createMessage(name,msg,date,id){
    let div=document.createElement("div")
    msgBox=`<span style="font-size:20px;padding: 5px;">From ${name} ${id}</span><span style="font-size:20px;width:96%;padding: 5px;">${msg}</span><span style="font-size:15px;width:96%;padding: 5px;">${new Date(date).toUTCString()}</span>`
    div.style.padding="9px"
    div.style.boxSizing="border-box"
    div.style.width="55%"
    div.style.boxShadow="5px 5px black"
    div.style.margin="10px"
    div.style.backgroundColor="whitesmoke"
    div.style.opacity=0.5
    div.style.display="flex"
    div.style.flexDirection="column"
    div.style.border="2px solid black"
    div.style.borderRadius="15px"
    div.innerHTML=msgBox
    message_area.appendChild(div)
    new Audio("/static/audio/notify.mp3").play()

    return div;
}

    function leftUser(name){
    notify=`<div style="font-size:20px;width:96%;padding: 5px;">${name} Left Meeting At ${new Date().toUTCString()}</div>`
    let div=document.createElement("div")
    div.innerHTML=notify
    div.style.backgroundColor="#e84118"
    div.style.border="1px solid black"
    div.style.borderRadius="15px"
    div.style.marginTop="10px"
    notification_area.appendChild(div)
    updateNotification()
        new Audio("/static/audio/notify.mp3").play()
}
function updateUser(){
    let member_count=members_list_area.childElementCount
    document.getElementById("member_count").innerHTML=member_count;
}
function deleteUser(id){
    document.getElementById(`${id}`).remove()
    updateUser();
    updateNotification()
}
function acceptStatus(status,id){
    socket.send(JSON.stringify({"action": "accept_request", "mid":mid, "id": id,"status":status}))
    deleteNotification(id)
    updateNotification()
}
function updateNotification(){
    let notify_count=notification_area.childElementCount
    document.getElementById("notify_count").innerHTML=notify_count;
}
function deleteNotification(id){
    document.getElementById(`${id}`).remove()
    updateNotification();
}
function createNotification(name,id){
    let notify=`<div style="font-size:20px;width:96%;padding: 5px;">${name} waiting in room are you accept his request</div>
<div style="display: flex"><button class="btn" onclick="acceptStatus(true,${id})">YES</button><button class="btn" onclick="acceptStatus(false,${id})">NO</button></div>`
    let div=document.createElement("div")
    div.innerHTML=notify
    div.style.backgroundColor="#e84118"
    div.style.border="1px solid black"
    div.style.borderRadius="15px"
    div.style.marginTop="10px"
    div.id=`${id}`
    notification_area.appendChild(div)
    updateNotification()
    new Audio("/static/audio/notify.mp3").play()
}
function addUserNotification(msg){
    let notify=`<div style="font-size:20px;width:96%;padding: 5px;">${msg}</div>`
    let div=document.createElement("div")
    div.innerHTML=notify
    div.style.backgroundColor="#e84118"
    div.style.border="1px solid black"
    div.style.borderRadius="15px"
    div.style.marginTop="10px"
    notification_area.appendChild(div)
    updateNotification()
    new Audio("/static/audio/notify.mp3").play()
}

function sendMessage(){
    let msg=document.getElementById("msg").value
    if(msg===""){
    document.getElementById("msg").click()
    }
    else{
        new Audio("/static/audio/notify.mp3").play()
    document.getElementById("msg").value=""
    socket.send(JSON.stringify({"action":"message","id":id,"mid":mid,"msg":msg}))}
}
function actionBlock(id){
    let e=document.getElementById(`btn${id}`)
    let task=e.getAttribute("task")
    socket.send(JSON.stringify({"action":task,"id":id,"host_id":pid,"mid":mid}))
    if(task==="block"){
        e.setAttribute("task","unblock")
        e.innerText="UnBlock"
    }
    else if(task==="unblock"){
        e.setAttribute("task","block")
        e.innerText="Block"
    }
}
function actionRemove(id){
    socket.send(JSON.stringify({"action":"remove","id":id,"host_id":pid,"mid":mid}))
}
function addUser(name,id){

    let notify=`<div style="font-size:20px;width:96%;padding: 5px;">${name} id ${id}</div>
${pid===parseInt(window.id.innerText) && pid!==id?`<div style="display: flex"><button class="btn" id="btn${id}" task="block" onclick="actionBlock(${id})">Block</button><button class="btn" task="remove" onclick="actionRemove(${id})">Remove</button></div>`:""}`
    let div=document.createElement("div")
    div.innerHTML=notify
    div.style.backgroundColor="#e84118"
    div.style.border="1px solid black"
    div.style.borderRadius="15px"
    div.style.marginTop="10px"
    div.id=`${id}`
    members_list_area.appendChild(div)
    updateUser()
    addUserNotification(`${name} Join Meeting At ${new Date().toUTCString()} id (${id})`)
}


window.moveTo(0, 0);
window.resizeTo(screen.availWidth, screen.availHeight);
window.addEventListener("keyup",(e)=>{
    if(e.key==="Enter"){
        sendMessage()
    }
})
document.getElementById("leave-meeting").addEventListener("click",()=> {
    location.href = "/leave/"
})
let notification_area=document.getElementsByClassName("notification-area")[0]
let message_area=document.getElementsByClassName("message")[0]
let members_list_area=document.getElementsByClassName("members-list-area")[0]
let send_btn=document.getElementById("send-btn")
let mid=JSON.parse(document.getElementById("mid").textContent)
let diff=JSON.parse(document.getElementById("diff").textContent)
let id=JSON.parse(document.getElementById("id").textContent)
let pid=JSON.parse(document.getElementById("pid").textContent)

send_btn.addEventListener("click",sendMessage)

// create connection with web socket

let socket=new WebSocket(`ws://${location.host}/ws/chatroom/`)

// when connect add on server as user

socket.onopen=()=>socket.send(JSON.stringify({"action":"entry",mid:mid,id:id}))

// when window or tab close

socket.onclose=()=>{location.href="/leave/"}

// method to get execute when server send some message

socket.onmessage=handleServerMessage


setTimeout(()=>{
location.href="/leave/"
},parseInt(diff)*1000);
