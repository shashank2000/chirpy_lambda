import React, { useState } from 'react';

const RGStatePanel = (props) => {	
	return (
		<div className="panel">
			<h3>RG State</h3>
			<table id="state-table">
			<tbody>
			{props.currMessage.rg_state && 
				Object.entries(props.currMessage.rg_state).map(elem => {
					const [ stateName, { value, falsy } ] = elem;
					return <tr key={stateName}>
						<td className="state-name">{stateName.replace("__", ".")}</td>
						<td className={`state-value ${falsy ? "falsy" : "truthy"}`}>{value}</td>
					</tr>;	
				})
			}
			</tbody>
			</table>
				
		</div>
	);
}

export default RGStatePanel;