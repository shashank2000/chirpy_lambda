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
	if (message.error) {
		message.source = "error";
	}
	console.log(message.error);
  	out.push(
		<div className={`message-container message-${message.source}`} key={idx}>
	  		<div className={`message message-${message.source} ${(props.activeMessage.text == message.text) ? "active" : "inactive"}`} onClick={e => props.activateMessage(message)} dangerouslySetInnerHTML={{__html: 
					(message.error || message.text).replace(/\s\s\s\s([^\n]*)/g, '\n<i class="errorLine">$1</i>;\n').replace(/\n/g, "<br />")   
	  		}}>
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
          <select className="subnode-picker" value={props.nextSupernode} onChange={e => {
              props.setNextSupernode(e.target.value);
          }}>
            {props.allSupernodes.map((supernodeName) => {
                return <option value={supernodeName} key={supernodeName}>{supernodeName}</option>;
            })}
          </select>
		</form>
	  </div>
   </div> 
  );
}

export default ChatBox;