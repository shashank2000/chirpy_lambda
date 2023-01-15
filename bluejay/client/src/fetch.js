const fetchResult = async (input, reset = false, kwargs = { }) => {
	let response = await fetch("/api/ping?" + new URLSearchParams({
	  	input ,
	  	reset ,
        kwargs : JSON.stringify(kwargs)
	}));
	if (response.status == 500) {
  	alert("Server error.");
  	return;
	}
	let data = await response.json();
	return data;
};

const fetchSupernodes = async () => {
    let response = await fetch("/api/supernodes");
    if (response.status == 500) {
      alert("Server error.");
      return;
    }
    let data = await response.json();
    return data;
};


export { fetchResult, fetchSupernodes };