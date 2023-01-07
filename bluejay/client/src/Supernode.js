import React, { useState } from 'react';

const Supernode = (props) => {
	return (
		<a className="node-container" onClick={props.onClickHandler}>
			<div className={`node ${(props.supernodeName == props.selectedSupernode) ? "open" : ""}`} key={props.supernodeName}>
				<span className={`node-name ${props.supernodeData.available ? "available" : "unavailable"}`}>
					{props.supernodeName}
				</span>
				{props.supernodeData.available && 
					<span className="node-label node-available">available</span>
				}
				{props.supernodeData.chosen && 
					<span className="node-label node-chosen">chosen</span>
				}
			</div>
			{(props.supernodeName == props.selectedSupernode) && 	
				<div className="entry-conditions">
					{(props.supernodeData.entry_conditions.length == 0) && <p className="entry-condition">No conditions found</p>}
					{props.supernodeData.entry_conditions.map(elem => {
						return <p key={elem.variable_name} className="entry-condition">
							{elem.verb}({elem.variable_name}:<span className="elem-val">{elem.val}</span>)
						</p>
					})}
				</div>
			}
		</a>
	);
}

const SupernodePanel = (props) => {
	const [selectedSupernode, setSelectedSupernode] = useState("");
	let supernodeList = [];
	const selectSupernode = (supernodeName) => {
		if (selectedSupernode != supernodeName) {
			setSelectedSupernode(supernodeName);
		} else {
			setSelectedSupernode();
		}
	}
	if (props.currMessage.supernodes) {
		for (const [supernodeName, supernodeData] of Object.entries(props.currMessage.supernodes)) {
			supernodeList.push(
				<Supernode supernodeName={supernodeName} supernodeData={supernodeData} selectedSupernode={selectedSupernode} onClickHandler={e => selectSupernode(supernodeName)}>
				</Supernode>
			)
		}	
	}
	return (
		<div className="panel">
			<h3>Supernodes</h3>
			{supernodeList}
		</div>
	);
}

export default SupernodePanel;