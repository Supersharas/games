//crazyTime = setInterval(refresh, 1000);
  function refresh(){
    fetch('/chess/lobby').then(response => response.json()).then(function(response){
      if(response.game.id){
        location = "chess/black/" + response.game.id;
      }
      //var newGame = document.getElementById('challange');
      //newGame.innerHTML = response.playerOne;
      //sessionStorage.setItem('userId', response.playerOne);
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
    if(!user){
      document.getElementById('cover').style.visibility = "visible";
      document.getElementById('notLogged').style.visibility = "visible";
    }
  }