import React, { useState } from 'react';

const Supernode = (props) => {
	return (
		<div className="supernode" key={props.supernodeName}>
			<span className="node-name">
				{props.supernodeName}
			</span>
			{props.supernodeData.available && 
				<span class="node-label node-available">available</span>
			}
			{props.supernodeData.chosen && 
				<span class="supernode-label supernode-chosen">chosen</span>
			}
		</div>
	);
}

const SupernodePanel = (props) => {
	let supernodeList = [];
	if (props.currMessage.supernodes) {
		for (const [supernodeName, supernodeData] of Object.entries(props.currMessage.supernodes)) {
			supernodeList.push(
				<Supernode supernodeName={supernodeName} supernodeData={supernodeData}>
				</Supernode>
			)
		}	
	}
	return (
		<div class="panel">
			<h3>supernodes</h3>
			{supernodeList}
		</div>
	);
}

export default SupernodePanel;