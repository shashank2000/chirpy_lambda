import { faSpinner } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import Link from 'next/link';
import React from 'react';

import { Message } from '@/types';

export interface ChatBoxProps {
  activeMessage?: Message;
  messages: Message[];
  activateMessage: (message: Message) => void;
  rerolloutToIdx: (idx: number) => void;
  copyToIdx: (idx: number) => void;
  onInput: React.FormEventHandler<HTMLFormElement>;
  message: string;
  setMessage: (message: string) => void;
  allSupernodes: string[];
  nextSupernode: string;
  setNextSupernode: (supernode: string) => void;
  messagesRef: React.RefObject<HTMLDivElement>;
}

export function ChatBox({
  activeMessage,
  messages,
  activateMessage,
  rerolloutToIdx,
  copyToIdx,
  onInput,
  message,
  setMessage,
  allSupernodes,
  nextSupernode,
  setNextSupernode,
  messagesRef
}: ChatBoxProps) {
  const out: JSX.Element[] = [];

  messages.forEach((message, idx) => {
    if (message.source == 'spin') {
      out.push(
        <div className="message-spin" key={idx}>
          <span className="reset-notice"> {message.text} </span>
          <FontAwesomeIcon icon={faSpinner} className="fa-spin" />
        </div>
      );
    } else if (message.text) {
      if (message.error) {
        message.source = 'error';
      }
      console.log(message.error);
      out.push(
        <div
          className={`message-container message-${message.source}`}
          key={idx}
        >
          <div
            role="presentation"
            className={`message message-${message.source} ${
              activeMessage?.text == message.text ? 'active' : 'inactive'
            }`}
            onClick={() => activateMessage(message)}
            dangerouslySetInnerHTML={{
              __html: (message.error || message.text)
                .replace(
                  /\s\s\s\s([^\n]*)/g,
                  '\n<i class="errorLine">$1</i>;\n'
                )
                .replace(/\n/g, '<br />')
            }}
          />

          {message.source == 'user' && (
            <Link
              className="rerollout"
              href="/#"
              onClick={() => rerolloutToIdx(idx)}
            >
              (rerollout to here)
            </Link>
          )}

          {message.source != 'user' && (
            <Link
              className="rerollout"
              href="/#"
              onClick={() => copyToIdx(idx)}
            >
              (copy to here)
            </Link>
          )}
        </div>
      );
    }
  });
  return (
    <div className="chat-container">
      <div className="messages" ref={messagesRef}>
        {out}
      </div>
      <div id="type-bar">
        <form onSubmit={onInput}>
          <input
            type="text"
            className="input"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="hi"
          />

          <select
            className="subnode-picker"
            value={nextSupernode}
            onChange={(e) => {
              setNextSupernode(e.target.value);
            }}
          >
            {allSupernodes.map((supernodeName) => {
              return (
                <option key={supernodeName} value={supernodeName}>
                  {supernodeName}
                </option>
              );
            })}
          </select>
        </form>
      </div>
    </div>
  );
}
