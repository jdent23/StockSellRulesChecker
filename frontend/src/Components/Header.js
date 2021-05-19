import React from 'react';
import { NavLink } from "react-router-dom";

export const Header = ()=> {
    return <div className="Header">
                <NavLink exact to="/" className="HeaderTab" style={{marginLeft: "3em"}} activeStyle={{background:"white"}}>
                        <h3 className="HeaderText">Market</h3>
                </NavLink>
                <NavLink to="/comparison" className="HeaderTab" activeStyle={{background:"white"}}>
                        <h3 className="HeaderText" style={{color:"black"}}>Comparison</h3>
                </NavLink>
                <div className="HeaderTab">
                    <h3 className="HeaderText" style={{color:"black"}}>Patterns</h3>
                </div>
           </div>
}