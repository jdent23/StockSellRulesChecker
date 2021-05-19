import React from 'react';
import { Market } from './Market';
import { Header } from './Header'
import { Comparison } from './Comparison';
import {
    BrowserRouter as Router,
    Switch,
    Route
  } from "react-router-dom";

export const Container = ()=> {
    return <div>
                <Router>
                    <Header/>
                    <div className="Container">
                            <Switch>
                                <Route exact path="/" component={Market} />
                                <Route path="/comparison" component={Comparison} />
                            </Switch>
                    </div>
                </Router>
           </div>
}