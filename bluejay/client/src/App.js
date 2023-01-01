import React, { useState } from 'react';
import RGStatePanel from './RGState';
import SubnodePanel from './Subnode';
import SupernodePanel from './Supernode';
import GenerationPanel from './Generation';


const ChatBox = (props) => {
  const out = [];
  
  for (const [idx, message] of props.messages.entries()) {
    if (message.source == "spin") {
      out.push(
        <div className="message-spin">
          <i className="fa fa-spinner fa-spin"></i>
        </div>
      ) 
    } else {
      out.push(
        <div className={`message message-${message.source} ${(props.activeMessage.text == message.text) ? "active" : "inactive"}`} key={idx} onClick={e => props.activateMessage(message)}>
          {message.text}
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

const ControlPanel = (props) => {
  return <div className="control-panel">
      <RGStatePanel currMessage={props.currMessage}/>
      <SubnodePanel currMessage={props.currMessage}/>
      <SupernodePanel currMessage={props.currMessage}/>
      <GenerationPanel currMessage={props.currMessage}/>
  </div>
}

const Main = (props) => {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [activeMessage, setActiveMessage] = useState({});
  // const [currMessage, setCurrMessage] = useState({
  //   "text": "this is a test",
  //   "subnodes": {
  //     "Global__Thingy": {
  //       "available": true,
  //       "chosen": true,
  //     },
  //     "Global__Thingy25": {
  //       "available": true,
  //       "chosen": false,
  //     }
  //   },
  //   "supernodes": {
  //     "FOOD_factoid": {
  //       "available": true,
  //       "chosen": true,
  //     },
  //     "GLOBALS": {
  //       "available": true,
  //       "chosen": false,
  //     }
  //   },
  // });

  const fetchResult = async (input) => {
    let response = await fetch("/api/ping?" + new URLSearchParams({
          input ,
    }));
    if (response.status == 500) {
      alert("Server error.");
      return;
    }
    let data = await response.json();
    return data;
  };
    
  const onInput = async (e) => {
    e.preventDefault();
    setMessages([...messages, {
      "text": message,
      "source": "user"
    }, {
      "text": "spin",
      "source": "spin",
    }])
    const submitted = message;
    setMessage("");
    const data = await fetchResult(submitted);
    if (data) {
      setMessages([...messages, {
          "text": message,
          "source": "user"
        }, {
          ...data,
          "source": "bot"
        }
      ]);  
    }
    
  }
  
  const activateMessage = (message) => {
    setActiveMessage(message);
  }
  
  return (
      <div class="container">
      <ChatBox messages={messages} message={message} setMessage={setMessage} onInput={onInput} activateMessage={activateMessage} activeMessage={activeMessage}/>
      <ControlPanel currMessage={activeMessage}/>
    </div>
  );
}

export default Main;