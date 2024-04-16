let transcript = document.querySelector('#para');
let text = transcript.textContent;

let list = text.split(" ")
let firstWord = (list)[0].toUpperCase();

// list[0].style.fontSize = 'Italic';
list[0] = firstWord;

text = list.join(" ");
transcript.textContent = text;
