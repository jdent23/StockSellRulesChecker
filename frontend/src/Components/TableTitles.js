import React, { Component } from 'react';

export class TableTitles extends Component {
    constructor(props) {
      super(props);
  
      this.onclick = function(ev) {
          console.log(ev.target.firstChild.data)
        this.props.notifyRule(ev.target.firstChild.data)
      }.bind(this)
  
    }

    render() {
        var columns = this.props.columns;
        return (
            <table style={{backgroud: "white"}}>
                <thead>
                    <tr onClick={this.onclick}>
                        {columns.map(col => <th style={{background: "#CCCCFF"}}>{col.split('_').join(' ')}</th>)}
                    </tr>
                </thead>
            </table>
        );
    }
  }