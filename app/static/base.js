
var slideOpen = false;
console.log(slideOpen);

function first(e){
  e.stopImmediatePropagation();
  this.removeEventListener("click", first);
}

function second(e) {
  document.querySelector('.slide').classList.remove('open');
  document.querySelector('.menuHolder').classList.remove("menuHolderOpen");
  e.stopImmediatePropagation();
  this.removeEventListener("click", second);
  slideOpen = false;
}

function openSlide() {
  if(slideOpen){
  	document.querySelector('.slide').classList.remove("open");
    document.querySelector('.menuHolder').classList.remove("menuHolderOpen");
  	slideOpen = false;
  } else {
  	document.querySelector('.slide').classList.add("open");
    document.querySelector('.menuHolder').classList.add("menuHolderOpen");
    document.addEventListener('click', first);
    document.addEventListener('click', second);
    slideOpen = true;
  }
}

function closeSlide() {
  document.querySelector('.slide').classList.remove("open");
  document.querySelector('.menuHolder').classList.remove("menuHolderOpen");
  slideOpen = false;
}

function SignIn() {
  document.getElementById('cover').style.visibility = "visible";
  document.getElementById('sign').style.visibility = "visible";
}
