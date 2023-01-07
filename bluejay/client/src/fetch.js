const fetchResult = async (input, reset = false) => {
	let response = await fetch("/api/ping?" + new URLSearchParams({
	  	input ,
	  	reset
	}));
	if (response.status == 500) {
  	alert("Server error.");
  	return;
	}
	let data = await response.json();
	return data;
};

export { fetchResult };