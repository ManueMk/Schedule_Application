console.log('CA MARCHE')
const elements=document.querySelectorAll(".cell")
console.log(elements)

for(let element of elements ){
	element.addEventListener("click",function(){
		const id = element.id
		console.log(id)


	})
}






function closeBox() {
	document.getElementById('box').style.top="-1000px";
}
	
	
function imprime(divName) {
      	var printContents = document.getElementById(divName).innerHTML;    
   		var originalContents = document.body.innerHTML;      
   		document.body.innerHTML = printContents;     
   		window.print();     
   		document.body.innerHTML = originalContents;
   }
