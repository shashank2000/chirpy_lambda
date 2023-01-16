import Link from 'next/link';

import { Message } from '@/types';

import { LogsPanel } from './logsPanel';
import PromptPanel from './promptPanel';
import RGStatePanel from './rgStatePanel';
import { SubnodePanel } from './subnodePanel';
import { SupernodePanel } from './supernodePanel';

export interface ControlPanelProps {
  currMessage?: Message;
  reset: () => void;
  resetAndRerollout: () => void;
}

export function ControlPanel({
  currMessage,
  reset,
  resetAndRerollout
}: ControlPanelProps) {
  return (
    <div className="control-panel">
      <div className="buttons">
        <Link className="reset-button button" href="/#" onClick={() => reset()}>
          Reset
        </Link>
        <Link
          className="reset-button button"
          href="/#"
          onClick={() => resetAndRerollout()}
        >
          Reset and Rerollout
        </Link>
        {currMessage && <LogsPanel currMessage={currMessage} />}
      </div>
      {currMessage && (
        <div className="panels">
          <SubnodePanel currMessage={currMessage} />
          {/* <GenerationPanel currMessage={currMessage}/> */}
          <SupernodePanel currMessage={currMessage} />
          <PromptPanel currMessage={currMessage} />
          <RGStatePanel currMessage={currMessage} />
        </div>
      )}
    </div>
  );
}
