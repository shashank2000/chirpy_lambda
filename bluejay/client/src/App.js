import React, { useState, useEffect } from 'react';
import { fetchResult, fetchSupernodes } from './fetch';
import ChatBox from './ChatBox';
import RGStatePanel from './RGState';
import SubnodePanel from './Subnode';
import SupernodePanel from './Supernode';
import PromptPanel from './Prompt';
import LogsPanel from './Logs';
import GenerationPanel from './Generation';

const START = "hi";

const ControlPanel = (props) => {
  return <div className="control-panel">
      <div className="buttons">
        <a className="reset-button button" href="#" onClick={e => props.reset()}>Reset</a>
        <a className="reset-button button" href="#" onClick={e => props.resetAndRerollout()}>Reset and Rerollout</a>
          <LogsPanel currMessage={props.currMessage}/>
      </div>
      <div className="panels">
        <SubnodePanel currMessage={props.currMessage}/>
        {/* <GenerationPanel currMessage={props.currMessage}/> */}
        <SupernodePanel currMessage={props.currMessage}/>
        <PromptPanel currMessage={props.currMessage}/>
        <RGStatePanel currMessage={props.currMessage}/>
      </div>
      

  </div>
}

const Main = (props) => {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [nextSupernode, setNextSupernode] = useState("");
  const [activeMessage, setActiveMessage] = useState({});
  const [firstRender, setFirstRender] = useState(true);
  const [handling, setHandling] = useState(false);
  const [unhandledMessages, setUnhandledMessages] = useState([]);
  

  const [allSupernodes, setAllSupernodes] = useState([""]); 

  const addMessage = async (msg) => {
    const reset = messages.length == 0;
    setMessages([...messages, {
      "text": msg,
      "source": "user"
    }, {
      "text": reset ? "Resetting Chirpy..." : "",
      "source": "spin",
    }]);  
    
    const submitted = msg;
    setMessage("");
    const data = await fetchResult(submitted, reset, { "prioritized_supernode" : nextSupernode });
    if (data) {
      setMessages([...messages, {
          "text": msg,
          "source": "user"
        }, {
          ...data,
          "source": "bot"
        }
      ]);
      activateMessage(data);
    }
    if (unhandledMessages.length) {
      unhandledMessages.shift(1);
      setHandling(false);
    }
  }
    
  const onFormSubmit = async (e) => {
    e.preventDefault();
    addMessage(message);
  }
  
  const activateMessage = (message) => {
    setActiveMessage(message);
  }
  
  const reset = async () => {
    messages.length = 0;
    setActiveMessage({});
    addMessage();
  };
  
  const resetAndRerollout = async () => {
    const userMessages = messages.filter(m => m.source == "user").map(m => m.text);  
    setActiveMessage({});
    setUnhandledMessages(userMessages);
    messages.length = 0;
  };
  
  const rerolloutToIdx = async (idx) => {
    console.log("Slicing to", idx);
    const userMessages = messages.slice(0, idx+1).filter(m => m.source == "user").map(m => m.text);  
    setUnhandledMessages(userMessages);
    messages.length = 0;
  };
  
  const populateSupernodes = async () => {
       const { supernodes } = await fetchSupernodes();
       setAllSupernodes(["", ...supernodes]);
  }
  
  useEffect(() => {
    if (firstRender) {
      populateSupernodes();
      reset();      
      setFirstRender(false);
    }
    
    if (unhandledMessages.length && !handling) {
      console.log(`We have to handle the following unhandled messages:`, unhandledMessages);
      const nextMessage = unhandledMessages[0];
      setHandling(true);
      addMessage(nextMessage);
    }
  });
  

  return (
      <div className="container">
      <ChatBox 
        messages={messages} 
        message={message}
        nextSupernode={nextSupernode}
        setNextSupernode={setNextSupernode}
        allSupernodes={allSupernodes}
        setMessage={setMessage}
        onInput={onFormSubmit}
        activateMessage={activateMessage}
        activeMessage={activeMessage}
        rerolloutToIdx={rerolloutToIdx}
      />
      <ControlPanel 
        currMessage={activeMessage} 
        reset={reset}
        resetAndRerollout={resetAndRerollout}
      />
    </div>
  );
}

export default Main;