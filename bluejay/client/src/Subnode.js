import React, { useState } from 'react';

const Subnode = (props) => {
	return (
		<div className="subnode" key={props.subnodeName}>
			<span className="subnode-name">
				{props.subnodeName}
			</span>
			{props.subnodeData.available && 
				<span class="subnode-label subnode-available">available</span>
			}
			{props.subnodeData.chosen && 
				<span class="subnode-label subnode-chosen">chosen</span>
			}
		</div>
	);
}

const SubnodePanel = (props) => {
	let subnodeList = [];
	if (props.currMessage.subnodes) {
		for (const [subnodeName, subnodeData] of Object.entries(props.currMessage.subnodes)) {
			subnodeList.push(
				<Subnode subnodeName={subnodeName} subnodeData={subnodeData}>
				</Subnode>
			)
		}	
	}
	return (
		<div class="panel">
			<h3>Subnodes</h3>
			{subnodeList}
		</div>
	);
}

export default SubnodePanel;