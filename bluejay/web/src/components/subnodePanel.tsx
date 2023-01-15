import { useState } from 'react';

import { Message, Subnode } from '@/types';

interface SubnodeComponentProps {
  subnodeName: string;
  subnodeData: Subnode;
  selectedSubnode?: string;
  onClickHandler: () => void;
}

function SubnodeComponent({
  subnodeName,
  subnodeData,
  selectedSubnode,
  onClickHandler
}: SubnodeComponentProps) {
  if (subnodeName == selectedSubnode) {
    console.log(subnodeData.entry_conditions);
  }
  return (
    <button className="node-container" onClick={onClickHandler}>
      <div
        className={`node ${subnodeName == selectedSubnode ? 'open' : ''}`}
        key={subnodeName}
      >
        <span
          className={`node-name ${
            subnodeData.available ? 'available' : 'unavailable'
          }`}
        >
          {subnodeName}
        </span>
        {subnodeData.available && (
          <span className="node-label node-available">available</span>
        )}
        {subnodeData.chosen && (
          <span className="node-label node-chosen">chosen</span>
        )}
      </div>
      {subnodeName == selectedSubnode && (
        <div className="entry-conditions">
          {subnodeData.entry_conditions.length == 0 && (
            <p className="entry-condition">No conditions found</p>
          )}
          {subnodeData.entry_conditions.map((elem) => {
            return (
              <p key={elem.variable_name} className="entry-condition">
                {elem.variable_name}:
                <span className="elem-val">{elem.val}</span>
              </p>
            );
          })}
        </div>
      )}
    </button>
  );
}

export interface SubnodePanelProps {
  currMessage: Message;
}

export function SubnodePanel({ currMessage }: SubnodePanelProps) {
  const [selectedSubnode, setSelectedSubnode] = useState<string>();

  const selectSubnode = (subnodeName: string) => {
    if (selectedSubnode != subnodeName) {
      setSelectedSubnode(subnodeName);
    } else {
      setSelectedSubnode(undefined);
    }
  };

  const { subnodes } = currMessage;

  return (
    <div className="panel">
      <h3>Subnodes</h3>
      {subnodes &&
        Object.entries(subnodes).map(([subnodeName, subnodeData]) => (
          <SubnodeComponent
            key={subnodeName}
            subnodeName={subnodeName}
            subnodeData={subnodeData}
            selectedSubnode={selectedSubnode}
            onClickHandler={() => selectSubnode(subnodeName)}
          />
        ))}
    </div>
  );
}
