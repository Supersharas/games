
var slideOpen = false;


function openSlide() {
  //document.getElementById('slide').style.left = '0';
  console.log('working');
  if(slideOpen){
  	document.querySelector('.slide').classList.remove("open");
  	slideOpen = false;
  } else {
  	document.querySelector('.slide').classList.add("open");
  	slideOpen = true;
  }
}