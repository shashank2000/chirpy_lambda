import React, { useState } from 'react';

import { Message, Supernode } from '@/types';

export interface SupernodeComponentProps {
  supernodeName: string;
  supernodeData: Supernode;
  selectedSupernode?: string;
  onClickHandler: () => void;
}

function SupernodeComponent({
  supernodeName,
  supernodeData,
  selectedSupernode,
  onClickHandler
}: SupernodeComponentProps) {
  return (
    <button className="node-container" onClick={onClickHandler}>
      <div
        className={`node ${supernodeName == selectedSupernode ? 'open' : ''}`}
        key={supernodeName}
      >
        <span
          className={`node-name ${
            supernodeData.available ? 'available' : 'unavailable'
          }`}
        >
          {supernodeName} ({supernodeData.score})
        </span>
        {supernodeData.available && (
          <span className="node-label node-available">available</span>
        )}
        {supernodeData.chosen && (
          <span className="node-label node-chosen">chosen</span>
        )}
      </div>
      {supernodeName == selectedSupernode && (
        <div className="entry-conditions">
          {supernodeData.entry_conditions.length == 0 && (
            <p className="entry-condition">No conditions found</p>
          )}
          {supernodeData.entry_conditions.map((elem) => {
            return (
              <p key={elem.variable_name} className="entry-condition">
                {elem.verb}({elem.variable_name}:
                <span className="elem-val">{elem.val}</span>)
              </p>
            );
          })}
        </div>
      )}
    </button>
  );
}

export interface SupernodePanelProps {
  currMessage: Message;
}

export function SupernodePanel({ currMessage }: SupernodePanelProps) {
  const [selectedSupernode, setSelectedSupernode] = useState<string>();

  const selectSupernode = (supernodeName: string) => {
    if (selectedSupernode != supernodeName) {
      setSelectedSupernode(supernodeName);
    } else {
      setSelectedSupernode(undefined);
    }
  };

  const { supernodes } = currMessage;

  return (
    <div className="panel">
      <h3>Supernodes</h3>
      {supernodes &&
        Object.entries(supernodes).map(([supernodeName, supernodeData]) => (
          <SupernodeComponent
            key={supernodeName}
            supernodeName={supernodeName}
            supernodeData={supernodeData}
            selectedSupernode={selectedSupernode}
            onClickHandler={() => selectSupernode(supernodeName)}
          ></SupernodeComponent>
        ))}
    </div>
  );
}
