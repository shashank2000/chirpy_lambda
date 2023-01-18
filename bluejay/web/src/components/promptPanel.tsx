import React, { useState } from 'react';

import { Message, Prompt } from '@/types';

export interface PromptComponentProps {
  promptName: string;
  promptData: Prompt;
  selectedPrompt?: string;
  onClickHandler: () => void;
}

export function PromptComponent({
  promptName,
  promptData,
  selectedPrompt,
  onClickHandler
}: PromptComponentProps) {
  return (
    <button className="node-container" onClick={onClickHandler}>
      <div
        className={`node ${promptName == selectedPrompt ? 'open' : ''}`}
        key={promptName}
      >
        <span
          className={`node-name ${
            promptData.available ? 'available' : 'unavailable'
          }`}
        >
          {promptName}
        </span>
        {promptData.available && (
          <span className="node-label node-available">available</span>
        )}
        {promptData.chosen && (
          <span className="node-label node-chosen">chosen</span>
        )}
      </div>
      {promptName == selectedPrompt && (
        <div className="entry-conditions">
          {promptData.entry_conditions.length == 0 && (
            <p className="entry-condition">No conditions found</p>
          )}
          {promptData.entry_conditions.map((elem) => {
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

export interface PromptPanelProps {
  currMessage: Message;
}

export function PromptPanel({ currMessage }: PromptPanelProps) {
  const [selectedPrompt, setSelectedPrompt] = useState<string>();

  const selectPrompt = (promptName: string) => {
    if (selectedPrompt != promptName) {
      setSelectedPrompt(promptName);
    } else {
      setSelectedPrompt(undefined);
    }
  };

  const { prompts } = currMessage;

  return (
    <div className="panel">
      <h3>Prompts</h3>
      {prompts &&
        Object.entries(prompts).map(([promptName, promptData]) => (
          <PromptComponent
            key={promptName}
            promptName={promptName}
            promptData={promptData}
            selectedPrompt={selectedPrompt}
            onClickHandler={() => selectPrompt(promptName)}
          ></PromptComponent>
        ))}
    </div>
  );
}

export default PromptPanel;
