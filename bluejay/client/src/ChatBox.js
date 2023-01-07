import React, { useState, useEffect } from 'react';

const ChatBox = (props) => {
  const out = [];
  
  for (const [idx, message] of props.messages.entries()) {
	if (message.source == "spin") {
	  out.push(
		<div className="message-spin" key={idx}>
		  <span className="reset-notice"> {message.text} </span>
		  <i className="fa fa-spinner fa-spin"></i>
		</div>
	  ) 
	} else if (message.text) {
	  out.push(
		<div className={`message-container message-${message.source}`} key={idx}>
		  <div className={`message message-${message.source} ${(props.activeMessage.text == message.text) ? "active" : "inactive"}`} onClick={e => props.activateMessage(message)}>
			{message.text}
		  </div>
		  {message.source == "user" && <a className="rerollout" href="#" onClick={e => props.rerolloutToIdx(idx)}>(rerollout to here)</a>}
		</div>
	  );
	}
  }
  return (
	<div className="chat-container">
	  <div className="messages">{out}</div>
	  <div id="type-bar">
		<form onSubmit={props.onInput}>
		  <input type="text" className="input" value={props.message} onChange={e => props.setMessage(e.target.value)} placeholder="hi"/>
		</form>
	  </div>
   </div> 
  );
}

export default ChatBox;