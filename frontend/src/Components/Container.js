import React, { Component } from 'react';
import { Market } from './Market';
import { Header } from './Header'
import { Comparison } from './Comparison';
import {
    BrowserRouter as Router,
    Switch,
    Route
  } from "react-router-dom";

export class Container extends Component {


    render() {
        return <div>
                    <Router>
                        <Header/>
                        <div className="Container">
                                <Switch>
                                    <Route exact path="/" component={ () => <Market notifyRule={this.props.notifyRule}/> } />
                                    <Route path="/comparison" component={ () => <Comparison notifyRule={this.props.notifyRule}/> } />
                                </Switch>
                        </div>
                    </Router>
            </div>
    }
}