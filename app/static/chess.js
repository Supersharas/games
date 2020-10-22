
var gamePrivacy;

//crazyTime = setInterval(refresh, 1000);
function refresh(){
  fetch('/chess/lobby').then(response => response.json()).then(function(response){
    if(response.game.id){
      location = "chess/black/" + response.game.id;
    }
  }).catch(function(err){
    console.log('err', err);
  })
}
// window.onload = crazyTime();
// function startGame(){
//   fetch('/game')
// }

// let user = sessionStorage.getItem('userId');
// window.onload = function(){
//   console.log('bla bla bla');
//   if(user){

//   }
// }
function startDialog() {
  console.log('user', user)
  if(user == '0' || user == 'Guest'){
    document.getElementById('cover').style.visibility = "visible";
    document.getElementById('notLogged').style.visibility = "visible";
  } else{
    ifPrivate();
  }
}

function closeDialog() {
  document.getElementById('cover').style.visibility = "hidden";
  document.getElementById('notLogged').style.visibility = "hidden";
  document.getElementById('ifPrivate').style.visibility = "hidden";
  document.getElementById('duration').style.visibility = "hidden";
  document.getElementById('waiting').style.visibility = "hidden";
}

function back(state) {
  if(state == 'ifPrivate'){
    closeDialog();
    startDialog();
  } else if(state == 'duration'){
    document.getElementById('ifPrivate').style.visibility = "visible";
    document.getElementById('duration').style.visibility = "hidden";
  }
}

function ifPrivate() {
  document.getElementById('notLogged').style.visibility = "hidden";
  document.getElementById('cover').style.visibility = "visible";
  document.getElementById('ifPrivate').style.visibility = "visible";
}

function openDuration(type) {
  gamePrivacy = type;
  document.getElementById('ifPrivate').style.visibility = "hidden";
  document.getElementById('duration').style.visibility = "visible";
}

function setDuration(duration) {
  duration = parseInt(duration)
  console.log(duration);
  if(Number.isInteger(duration)){
    document.getElementById('duration').style.visibility = "hidden";
    document.getElementById('waiting').style.visibility = "visible";
    fetchPost('/chess/commence', {gamePrivacy: gamePrivacy, duration:
    duration}).then(function(response){
      console.log('response', response);
      if(response.status == 'redirect'){
        window.location.href = 'chess/white/' + response.id;
      } else if(response.status == 'waiting'){
        matchTime = setInterval(checkMatch, 2000, response.offerId);
      }
    })
  }
}

document.onkeydown = function(evt) {
  evt = evt || window.event;
  if (evt.keyCode == 27) {
      closeDialog();
  }
};

function checkMatch(offid){
  fetchPost('/chess/lobby', {offerId: offid}).then(function(response){
    console.log(response);
    if(response.url){
      location = response.url;
    }
  })
}

function fetchPost(address, message){
  return fetch(address,{
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: JSON.stringify(message)
  }).then(response => response.json()).then(function(response){
    return response
  })
}