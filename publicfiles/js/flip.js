let card = document.getElementById("card");
let card2 = document.getElementById("card2");

const flip = () => {
  card2.style.display = "flex";
  card.style.animation = "animate2 0.5s linear  forwards";
  card2.style.animation = "animate 0.5s linear 0.5s forwards";
};

const flipBack = () => {
  card.style.transform = "rotateY(90deg)";
  card.style.animation = "animate 0.5s linear 0.5s forwards";
  card2.style.animation = "animate2 0.5s linear forwards";
};