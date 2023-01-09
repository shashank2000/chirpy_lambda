import React, { useState } from 'react';

const Prompt = (props) => {
	return (
		<a className="node-container" onClick={props.onClickHandler}>
			<div className={`node ${(props.promptName == props.selectedPrompt) ? "open" : ""}`} key={props.promptName}>
				<span className={`node-name ${props.promptData.available ? "available" : "unavailable"}`}>
					{props.promptName}
				</span>
				{props.promptData.available && 
					<span className="node-label node-available">available</span>
				}
				{props.promptData.chosen && 
					<span className="node-label node-chosen">chosen</span>
				}
			</div>
			{(props.promptName == props.selectedPrompt) && 	
				<div className="entry-conditions">
					{(props.promptData.entry_conditions.length == 0) && <p className="entry-condition">No conditions found</p>}
					{props.promptData.entry_conditions.map(elem => {
						return <p key={elem.variable_name} className="entry-condition">
							{elem.verb}({elem.variable_name}:<span className="elem-val">{elem.val}</span>)
						</p>
					})}
				</div>
			}
		</a>
	);
}

const PromptPanel = (props) => {
	const [selectedPrompt, setSelectedPrompt] = useState("");
	let promptList = [];
	const selectPrompt = (promptName) => {
		if (selectedPrompt != promptName) {
			setSelectedPrompt(promptName);
		} else {
			setSelectedPrompt();
		}
	}
	if (props.currMessage.prompts) {
		for (const [promptName, promptData] of Object.entries(props.currMessage.prompts)) {
			promptList.push(
				<Prompt key={promptName} promptName={promptName} promptData={promptData} selectedPrompt={selectedPrompt} onClickHandler={e => selectPrompt(promptName)}>
				</Prompt>
			)
		}	
	}
	return (
		<div className="panel">
			<h3>Prompts</h3>
			{promptList}
		</div>
	);
}

export default PromptPanel;