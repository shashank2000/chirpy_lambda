import Link from 'next/link';
import React from 'react';

import { Message } from '@/types';

function escapeHtml(unsafe: string) {
  return unsafe
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

export interface LogsPanelProps {
  currMessage: Message;
}

export function LogsPanel({ currMessage }: LogsPanelProps) {
  const openLogs = () => {
    const full_logs = currMessage.full_logs ?? [];
    let msg = full_logs.map((log) => escapeHtml(log)).join('<br/><br/>');
    msg = msg.replace('\n', '<br/>');

    const wnd = window.open('about:blank', '', '_blank');
    if (wnd) wnd.document.write(msg);
  };

  return (
    <Link onClick={openLogs} className="logs-button button" href="/#">
      Logs
    </Link>
  );
}
