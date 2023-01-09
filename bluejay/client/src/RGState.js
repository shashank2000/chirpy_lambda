import React, { useState } from 'react';

const RGStatePanel = (props) => {
	console.log(props.currMessage.rg_state);
	
	const isFalsy = (s) => {
		return (s === "None" || s === "False" || s === "0");
	}
	return (
		<div className="panel">
			<h3>RG State</h3>
			<table id="state-table">
			<tbody>
			{props.currMessage.rg_state && 
				Object.entries(props.currMessage.rg_state).map(elem => {
					const [ stateName, stateValue ] = elem;
					return <tr key={stateName}>
						<td className="state-name">{stateName.replace("__", ".")}</td>
						<td className={`state-value ${isFalsy(stateValue) ? "falsy" : "truthy"}`}>{stateValue}</td>
					</tr>;	
				})
			}
			</tbody>
			</table>
				
		</div>
	);
}

export default RGStatePanel;