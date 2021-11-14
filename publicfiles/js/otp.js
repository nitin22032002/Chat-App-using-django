async function verify(e){
    res=await fetch(`/adduser/?otp=${document.getElementById("otp").value}`)
    res=await res.json()
    console.log(res)
    if(res.status)
        location.href="/"
    else{
        document.getElementById("alert").innerHTML="Invalid OTP"
    }
}
document.getElementById("resend").addEventListener("click",()=>location.href="/resend/")
document.getElementById("verify").addEventListener("click",verify)
