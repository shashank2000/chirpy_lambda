import React, { useState } from 'react';

const escapeHtml = (unsafe) => {
    return unsafe.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
}

const LogsPanel = (props) => {
	console.log(props.currMessage.rg_state);
	
	const openLogs = () => {
		console.log("openLogs");
		let msg = props.currMessage.full_logs.map((log) => escapeHtml(log)).join("<br/><br/>");
		msg = msg.replace("\n", "<br/>");
		
		var wnd = window.open("about:blank", "", "_blank");
		wnd.document.write(msg);
   }
	
	
	return (
		<a onClick={openLogs} className="logs-button button" href="#">
			Logs
		</a>
	);
}

export default LogsPanel;