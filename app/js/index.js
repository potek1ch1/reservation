const submit = document.getElementById("submit");
const username = document.getElementsByName("username");
const password = document.getElementsByName("password");

submit.addEventListener("ciick", ()=>{
  console.log(username);
  console.log(password);
})