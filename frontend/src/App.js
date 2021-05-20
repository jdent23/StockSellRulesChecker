import logo from './logo.svg';
import React, { Component } from 'react';
import './App.css';
import { Container } from './Components/Container'
import { MarketDirection } from './Components/MarketDirection'
import { Notifier } from './Components/Notifier'

export class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      notify_function: function(content) {},
      rules: {}
    };

    this.changeNotifyFunction = function(new_notify_function) {
      this.setState({notify_function: new_notify_function})
    }.bind(this);

    this.notifyRule = function(rule_name) {
      if(rule_name in this.state.rules) {
        this.state.notify_function(
          <div>
            <h3>{rule_name}: {this.state.rules[rule_name]["tier"]} Tier</h3>

            <div className="NotifierContent">
              <p>{this.state.rules[rule_name]["summary"]}</p>
            </div>
          </div>
        )
      } else {
        this.state.notify_function(
          <div>
            <h3>{rule_name}</h3>

            <div className="NotifierContent">
              <p>Rule not documented</p>
            </div>
          </div>
        )
      }
    }.bind(this);
  }

  componentDidMount() {
    this.setState({ isLoading: true });
 
    fetch("http://localhost:5000/api/rules")
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong ...');
        }
      })
      .then(res => this.setState({rules: res}))
      .catch(error => this.setState({ error }));
  }

  render() {
  return <div className="App">
          <Notifier changeNotifyFunction={this.changeNotifyFunction}/>
          <div className="Title">
            <h1 className="TitleText">Stock Sell Rules Checker</h1>
          </div>
          <MarketDirection notifyRule={this.notifyRule}/>
          <Container notifyRule={this.notifyRule}/>
        </div>
  }
}

export default App;
