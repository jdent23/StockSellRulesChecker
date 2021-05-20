import React, { Component } from 'react';
import { TableTitles } from './TableTitles';
import { TableData } from './TableData';
import { SearchOptions } from './SearchOptions';
import { ApplyFilter } from './SearchOptions';

export class Notifier extends Component {
    constructor(props) {
        super(props);
        this.state = {
          style: {visibility: "hidden"},
          content: <div>This is great content</div>
        };

        this.closeNotification = function() {
            this.setState({style: {visibility: "hidden"}})
            console.log(this.state)
        }.bind(this);
    
        this.Notify = function(content) {
          this.setState({content: content, style: {visibility: "visible"}})
        }.bind(this);

        this.props.changeNotifyFunction(this.Notify)
      }

  render() {

    return <div className="Notifier" style={this.state.style}>
        {this.state.content}
        <button type="button" onClick={this.closeNotification}>Close</button>
    </div>
  }
}
