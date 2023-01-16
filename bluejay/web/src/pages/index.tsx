import Head from 'next/head';
import Image from 'next/image';
import Link from 'next/link';
import { FormEventHandler, useEffect, useRef, useState } from 'react';

import { ChatBox } from '@/components/chatBox';
import { ControlPanel } from '@/components/controlPanel';
import { Message } from '@/types';
import { fetchResult, fetchSupernodes } from '@/utils/fetch';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [message, setMessage] = useState('');
  const [activeMessage, setActiveMessage] = useState<Message>();
  const [firstRender, setFirstRender] = useState(true);
  const [handling, setHandling] = useState(false);
  const [unhandledMessages, setUnhandledMessages] = useState<string[]>([]);
  const [nextSupernode, setNextSupernode] = useState('');
  const [allSupernodes, setAllSupernodes] = useState(['']);

  const messagesRef = useRef<HTMLDivElement>(null);

  const addMessage = async (msg: string | undefined) => {
    const reset = messages.length == 0;
    setMessages([
      ...messages,
      ...(msg
        ? [
            {
              text: msg,
              source: 'user'
            }
          ]
        : []),
      {
        text: reset ? 'Resetting Chirpy...' : '',
        source: 'spin'
      }
    ]);

    const submitted = msg;
    setMessage('');
    const data = await fetchResult(submitted, reset, {
      prioritized_supernode: nextSupernode
    });
    if (data) {
      setMessages([
        ...messages,
        {
          text: msg,
          source: 'user'
        },
        {
          ...data,
          source: 'bot'
        }
      ]);
      activateMessage(data);
    }
    if (unhandledMessages.length) {
      unhandledMessages.shift();
      setHandling(false);
    }
  };

  const onFormSubmit: FormEventHandler<HTMLFormElement> = async (e) => {
    e.preventDefault();
    addMessage(message);
  };

  const activateMessage = (message: Message) => {
    setActiveMessage(message);
  };

  const reset = async () => {
    messages.length = 0;
    setActiveMessage(undefined);
    addMessage(undefined);
  };

  const resetAndRerollout = async () => {
    const userMessages = messages
      .filter((m) => m.source == 'user')
      .map((m) => m.text);
    setActiveMessage(undefined);
    setUnhandledMessages(userMessages);
    messages.length = 0;
  };

  const rerolloutToIdx = async (idx: number) => {
    console.log('Slicing to', idx);
    const userMessages = messages
      .slice(0, idx + 1)
      .filter((m) => m.source == 'user')
      .map((m) => m.text);
    setUnhandledMessages(userMessages);
    messages.length = 0;
  };
  
  const copyToIdx = async (idx: number) => {
      console.log('Copying to', idx);
      const userMessages = messages
        .slice(0, idx + 1)
        .filter((m) => (m.text && m.text != "undefined"))
        .map((m) => (m.source == "user" ? "🤗" : "🦜") + " "+ m.text.replace("> ", "") + (m.error ? "\n\n⚠️⚠️⚠️ERROR⚠️⚠️⚠️\n" + m.error : ""))
        .join("\n");
      navigator.clipboard.writeText(userMessages);
    };

  const populateSupernodes = async () => {
    const result = await fetchSupernodes();
    if (!result) return;
    const { supernodes } = result;
    setAllSupernodes(['', ...Array.from(new Set(supernodes))]);
  };

  useEffect(() => {
    if (firstRender) {
      populateSupernodes();
      reset();
      setFirstRender(false);
    }

    if (unhandledMessages.length && !handling) {
      console.log(
        `We have to handle the following unhandled messages:`,
        unhandledMessages
      );
      const nextMessage = unhandledMessages[0];
      setHandling(true);
      addMessage(nextMessage);
    }
  });

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <>
      <Head>
        <title>Bluejay</title>
      </Head>
      <nav>
        <Image src="/bluejay.png" alt="Bluejay" width={35} height={35} />
        <Link className="item" href="/#">
          <h1>Bluejay</h1>
        </Link>
        <Link className="item pull-right" href="/#">
          Signout
        </Link>
      </nav>
      <div className="container">
        <ChatBox
          messages={messages}
          message={message}
          setMessage={setMessage}
          onInput={onFormSubmit}
          activateMessage={activateMessage}
          activeMessage={activeMessage}
          rerolloutToIdx={rerolloutToIdx}
          copyToIdx={copyToIdx}
          nextSupernode={nextSupernode}
          setNextSupernode={setNextSupernode}
          allSupernodes={allSupernodes}
          messagesRef={messagesRef}
        />
        <ControlPanel
          currMessage={activeMessage}
          reset={reset}
          resetAndRerollout={resetAndRerollout}
        />
      </div>
    </>
  );
}
