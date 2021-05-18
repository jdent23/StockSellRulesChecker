import React from 'react';

export const Header = ()=> {
    return <div className="Header">
                <div className="HeaderTab" style={{width : '6em', marginLeft: "3em"}}>
                    <h3 className="HeaderText">Market</h3>
                </div>
                <div className="HeaderTab" style={{width : '10em'}}>
                    <h3 className="HeaderText">Comparison</h3>
                </div>
                <div className="HeaderTab" style={{width : '8em'}}>
                    <h3 className="HeaderText">Patterns</h3>
                </div>
           </div>
}