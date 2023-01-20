import { Message } from '@/types';

export interface RGStatePanelProps {
  currMessage: Message;
}

export function RGStatePanel({ currMessage }: RGStatePanelProps) {
  console.log(currMessage.rg_state);

  return (
    <div className="panel">
      <h3>RG State</h3>
      <table id="state-table">
        <tbody>
          {currMessage.rg_state &&
            Object.entries(currMessage.rg_state).map((elem) => {
              const [stateName, { value, falsy }] = elem;
              return (
                <tr key={stateName}>
                  <td className="state-name">{stateName.replace('__', '.')}</td>
                  <td className={`state-value ${falsy ? 'falsy' : 'truthy'}`}>
                    {value}
                  </td>
                </tr>
              );
            })}
        </tbody>
      </table>
    </div>
  );
}

export default RGStatePanel;
