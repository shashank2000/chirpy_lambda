import React, { useState } from 'react';

const Subnode = (props) => {
	if (props.subnodeName == props.selectedSubnode) {
		console.log(props.subnodeData.entry_conditions);
	}
	return (
		<a className="node-container" onClick={props.onClickHandler}>
			<div className={`node ${(props.subnodeName == props.selectedSubnode) ? "open" : ""}`} key={props.subnodeName}>
				<span className={`node-name ${props.subnodeData.available ? "available" : "unavailable"}`}>
					{props.subnodeName}
				</span>
				{props.subnodeData.available && 
					<span className="node-label node-available">available</span>
				}
				{props.subnodeData.chosen && 
					<span className="node-label node-chosen">chosen</span>
				}
			</div>
			{(props.subnodeName == props.selectedSubnode) && 	
				<div className="entry-conditions">
					{(props.subnodeData.entry_conditions.length == 0) && <p className="entry-condition">No conditions found</p>}
					{props.subnodeData.entry_conditions.map(elem => {
						return <p key={elem.variable_name} className="entry-condition">
							{elem.variable_name}:<span className="elem-val">{elem.val}</span>
						</p>
					})}
				</div>
			}
		</a>
	);
}

const SubnodePanel = (props) => {
	const [selectedSubnode, setSelectedSubnode] = useState("");
	let subnodeList = [];
	const selectSubnode = (subnodeName) => {
		if (selectedSubnode != subnodeName) {
			setSelectedSubnode(subnodeName);
		} else {
			setSelectedSubnode();
		}
	}
	if (props.currMessage.subnodes) {
		for (const [subnodeName, subnodeData] of Object.entries(props.currMessage.subnodes)) {
			subnodeList.push(
				<Subnode subnodeName={subnodeName} subnodeData={subnodeData} selectedSubnode={selectedSubnode} onClickHandler={e => selectSubnode(subnodeName)}>
				</Subnode>
			)
		}	
	}
	return (
		<div className="panel">
			<h3>Subnodes</h3>
			{subnodeList}
		</div>
	);
}

export default SubnodePanel;